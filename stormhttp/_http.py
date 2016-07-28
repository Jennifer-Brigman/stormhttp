import httptools

from ._status import *
from ._cookies import *

# Global Variables
__all__ = [
    "HTTPHeaders",
    "HTTPRequest",
    "HTTPResponse",
    "HTTPMessage",
    "HTTPErrorResponse"
]


class HTTPHeaders(collections.MutableMapping):
    def __init__(self, headers: typing.Mapping[str, str]):
        self._headers = dict()
        for name, value in headers.items():
            self._headers[name] = value

    def __repr__(self) -> str:
        return "<HTTPHeaders {}>".format(", ".join(
            ["{}: {}".format(name, value) for name, value in self._headers.items()]
        ))

    def __setitem__(self, key: str, value: str) -> None:
        self._headers[key] = value

    def __getitem__(self, key: str) -> str:
        _key = key.lower()
        for header_key in self._headers:
            if _key == header_key.lower():
                return self._headers[header_key]
        raise KeyError("{}".format(key))

    def __delitem__(self, key: str) -> None:
        for k in self._headers.keys():
            if k.lower() == key.lower():
                del self._headers[k]
                break
        else:
            raise KeyError(str(key))

    def __len__(self) -> int:
        return len(self._headers)

    def __iter__(self):
        return iter(self._headers)

    def __contains__(self, item) -> bool:
        try:
            self.__getitem__(item)
            return True
        except KeyError:
            return False

    def to_header(self) -> str:
        """
        Converts the headers to a string to be sent.
        :return: The headers as a string.
        """
        return "\r\n".join(["%s: %s" % (name, value) for name, value in self._headers.items()])


class HTTPMessage:
    def __init__(self):
        self.headers = HTTPHeaders({})
        self.cookies = HTTPCookies(b'')
        self.url = None
        self.method = None
        self.body = b""
        self.version = b""
        self.url_bytes = ""

        self._header_buffer = []
        self._is_complete = False

    def __repr__(self) -> str:
        return "<HTTPMessage method: {}, url: {}, headers: {}>".format(self.method, self.url, self.headers)

    def on_url(self, url: bytes) -> None:
        """
        If the URL hasn't been resolved yet, resolve it here.
        :param url: URL to resolve.
        :return: None
        """
        if url != b'':
            self.url_bytes = url.decode("utf-8")
            self.url = httptools.parse_url(url)

    def on_header(self, name: typing.Union[bytes, None], value: typing.Union[bytes, None]) -> None:
        """
        Function that is called on each fragment of a header that is read.
        :param name: Name of the value of the key value pair.
        :param value: Value of the key value pair.
        :return: None
        """
        self._header_buffer.append((name, value))

    def on_headers_complete(self) -> None:
        """
        Function that's called once all headers are processed.
        This function compiles all previous header entries to
        a bunch of key-value pairs. Also calculates cookies.
        :return: None
        """
        _headers = {}
        _buf = None
        _buf_done = False
        _cookies = b''
        for name, value in self._header_buffer:
            if name is not None:
                if _buf_done or _buf is None:
                    if _buf == b'Cookie':
                        _cookies += _headers[b'Cookie']
                        del _headers[b'Cookie']
                    _buf = name
                    _buf_done = False
                else:
                    _buf += name
            if value is not None:
                if _buf not in _headers:
                    _headers[_buf] = value
                else:
                    _headers[_buf] += value
                _buf_done = True
        if b'Cookie' in _headers:
            _cookies = _headers[b'Cookie']
            del _headers[b'Cookie']

        self.headers = HTTPHeaders({key.decode("utf-8"): value.decode("utf-8") for key, value in _headers.items()})
        self.cookies = HTTPCookies(_cookies)

    def on_body(self, body: bytes) -> None:
        """
        When bytes are added to the body this is called.
        :param body: Bytes to add to the body.
        :return: None
        """
        self.body += body

    def on_message_complete(self) -> None:
        """
        Once the message is complete, set the flag.
        :return: None
        """
        self._is_complete = True
        self.body = self.body.decode("utf-8")

    def is_complete(self) -> bool:
        """
        Returns True if the message is complete.
        :return:
        """
        return self._is_complete

    def to_bytes(self) -> bytes:
        """
        Convert the message to bytes.
        :return: Bytes to send/receive.
        """
        raise NotImplementedError("HTTPMessage.to_bytes() is not implemented.")


class HTTPResponse(HTTPMessage):
    def __init__(self):
        HTTPMessage.__init__(self)
        self.status_code = 200
        self.headers = HTTPHeaders({})

    def __setattr__(self, key: str, value) -> None:
        if key == "status_code":
            if not isinstance(value, int) or value not in STATUS_CODES:
                raise ValueError("{} is not a valid HTTP status code.".format(repr(value)))
        super(HTTPMessage, self).__setattr__(key, value)

    def to_bytes(self) -> bytes:
        """
        Converts the HTTPResponse to bytes.
        :return: Bytes to send.
        """
        response_parts = ["HTTP/%s %d %s" % (self.version, self.status_code, STATUS_CODES[self.status_code])]
        header_bytes = self.headers.to_header()
        if len(header_bytes) > 0:
            response_parts.append(header_bytes)
        cookie_bytes = self.cookies.to_header(set_cookie=True)
        if len(cookie_bytes) > 0:
            response_parts.append(cookie_bytes)
        if isinstance(self.body, str):
            response_parts.extend(["", self.body])
            return "\r\n".join(response_parts).encode("utf-8")
        else:
            return "\r\n".join(response_parts).encode("utf-8") + b'\r\n\r\n' + self.body


class HTTPRequest(HTTPMessage):
    def __init__(self):
        HTTPMessage.__init__(self)
        self.match_info = {}
        self.app = None

    def to_bytes(self) -> bytes:
        """
        Converts the HTTPRequest to bytes.
        :return: Bytes received.
        """
        request_parts = ['%s %s HTTP/%s' % (self.method, self.url_bytes, self.version)]
        header_bytes = self.headers.to_header()
        if len(header_bytes) > 0:
            request_parts.append(header_bytes)
        if len(self.cookies) > 0:
            request_parts.append(self.cookies.to_header())
        request_parts.extend(['', self.body])
        return '\r\n'.join(request_parts).encode("utf-8")

    def decorate_response(self, response: HTTPResponse) -> HTTPResponse:
        """
        Decorates a response with the required information that
        the response needs from the HTTPRequest.
        :param response: Response to decorate.
        :return: Decorated response.
        """
        response.cookies = self.cookies
        response.version = self.version
        return response


class HTTPErrorResponse(HTTPResponse):
    def __init__(self, error: int):
        HTTPResponse.__init__(self)
        self.status_code = error
        self.body = ""

