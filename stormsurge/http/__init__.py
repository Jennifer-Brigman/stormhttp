import asyncio
import collections
import datetime
import httptools
import re
import socket
import typing
import stormsurge.http.status


# Global Variables
__all__ = [
    "HTTPCookie",
    "HTTPCookies",
    "HTTPHeaders",
    "HTTPRequest",
    "HTTPResponse",
    "HTTPMessage",
    "receive_client"
]
_QVALUE_REGEX = re.compile(b'^\\s?([^;]+)(?:;q=(\\d\\.\\d)|;level=\\d+)+?$')
_COOKIE_REGEX = re.compile(b'([^\s=;]+)(?:=([^=;]+))?(?:;|$)')
_COOKIE_EXPIRE_FORMAT = "%a, %d %b %Y %H:%M:%S UTC"
_COOKIE_EXPIRE_TIME = datetime.datetime.fromtimestamp(1)


class HTTPCookie(collections.MutableMapping):
    def __init__(self, raw_cookie: bytes):
        self._expires = None
        self._http_only = False
        self._secure = False
        self._values = {}
        self._changed = False
        for key, value in _COOKIE_REGEX.findall(raw_cookie):
            if key == b'HttpOnly' and value == b'':
                self._http_only = True
            elif key == b'Secure' and value == b'':
                self._secure = True
            elif key == b'Expires':
                try:
                    self._expires = datetime.datetime.strptime(value.decode("latin-1"), _COOKIE_EXPIRE_FORMAT)
                except (ValueError, UnicodeDecodeError):
                    self._expires = None
            else:
                self._values[key] = value

    def __getitem__(self, item: bytes) -> bytes:
        return self._values[item]

    def __setitem__(self, key: bytes, value: bytes) -> None:
        if key == b'Expires':
            raise ValueError("Set cookie expire times through HTTPCookie.set_expire_time().")
        self._values[key] = value
        self._changed = True

    def __len__(self) -> int:
        return len(self._values)

    def __delitem__(self, item: bytes):
        del self._values[item]

    def __contains__(self, item: bytes):
        return item in self._values

    def __iter__(self):
        return iter(self._values)

    def expire_cookie(self) -> None:
        """
        Manually expires a cookie before it's expiry time.
        Also removes all key-value pairs.
        :return: None
        """
        self.set_expire_time(_COOKIE_EXPIRE_TIME)
        for key, value in self._values.items():
            self._values[key] = b''
        self._changed = True

    def is_expired(self) -> bool:
        """
        Checks to see if the cookie is expired. If there is
        no Expires field in the cookie, then the cookie will
        never expire.
        :return: If the cookie is expired, return True.
        """
        return self._expires is not None and self._expires < datetime.datetime.utcnow()

    def set_expire_time(self, expire: datetime.datetime) -> None:
        """
        Sets a new expire time for the cookie.
        :param expire: Datetime when the cookie should expire. Should be in UTC.
        :return: None
        """
        if not isinstance(expire, datetime.datetime):
            raise ValueError("Argument to HTTPCookie.set_expire_time() must be a datetime.datetime object.")
        self._changed |= expire != self._expires
        self._expires = expire

    def get_expire_time(self) -> datetime.datetime:
        """
        Gets the datetime object associated with the cookie's expire time.
        :return: Datetime object.
        """
        return self._expires

    def set_http_only(self, http_only: bool) -> None:
        """
        Sets the status of HttpOnly for the cookie which
        makes the cookie only accessible via HTTP and not Javascript.
        :param http_only: True if HttpOnly should be added to the cookie.
        :return: None
        """
        if not isinstance(http_only, bool):
            raise ValueError("Argument to HTTPCookie.set_http_only() must be a bool.")
        self._changed |= self._http_only != http_only
        self._http_only = http_only

    def is_http_only(self) -> bool:
        """
        Checks to see if the cookie has the HttpOnly flag.
        :return: True if the cookie is HttpOnly, False otherwise.
        """
        return self._http_only

    def set_secure(self, secure: bool) -> None:
        """
        Sets the Secure status for the cookie which restricts
        the cookie to only be transmitted via HTTPS.
        :param secure: True if Secure should be added to the cookie.
        :return: None
        """
        if not isinstance(secure, bool):
            raise ValueError("Argument to HTTPCookie.set_secure() must be a bool.")
        self._changed |= secure != self._secure
        self._secure = secure

    def is_secure(self) -> bool:
        """
        Checks to see if the cookie has the Secure flag.
        :return: True if the cookie is Secure, False otherwise.
        """
        return self._secure

    def is_changed(self) -> bool:
        """
        Checks to see if the cookie has changed since being read.
        :return:
        """
        return self._changed

    def to_bytes(self, set_cookie=False) -> bytes:
        """
        Converts the cookie into a HTTP header entry.
        :param set_cookie: If True, exports the cookie as a Set-Cookie header.
        :return: Bytes to add as a single header entry.
        """
        cookie_bytes = b'Cookie: %b;%b%b%b' % (
            b'; '.join(b'%b=%b' % (key, value) for key, value in self._values.items()),
            b' Expires=%b;' % self._expires.strftime(_COOKIE_EXPIRE_FORMAT).encode("latin-1") if self._expires is not None else b'',
            b' HttpOnly;' if self._http_only else b'',
            b' Secure;' if self._secure else b''
        )
        if set_cookie:
            cookie_bytes = b'Set-' + cookie_bytes
        return cookie_bytes


class HTTPCookies:
    def __init__(self, raw_cookies: typing.List[bytes]):
        self._cookies = []
        for cookie in raw_cookies:
            self._cookies.append(HTTPCookie(cookie))

    def to_bytes(self, set_cookies=False) -> bytes:
        """
        Converts a collection of cookies into bytes similar to
        HTTPHeaders. Option to convert to Set-Cookie headers
        to modify cookies that have been changed.
        :param set_cookies: If True, is exporting Set-Cookie headers.
        :return: Bytes to add to a request/response as headers.
        """
        cookie_bytes = b'\r\n'.join([cookie.to_bytes(set_cookie=set_cookies) for cookie in self._cookies if (cookie.is_changed() or not set_cookies)])
        if len(cookie_bytes) > 0:
            cookie_bytes += b'\r\n'
        return cookie_bytes


class HTTPHeaders(collections.MutableMapping):
    def __init__(self, headers: typing.Mapping[bytes, bytes]):
        self._headers = dict()
        for name, value in headers.items():
            self._headers[name] = value

    def __repr__(self) -> str:
        return "<HTTPHeaders {}>".format(", ".join(
            ["{}: {}".format(name, value) for name, value in self._headers.items()]
        ))

    def __setitem__(self, key: bytes, value: bytes) -> None:
        self._headers[key] = value

    def __getitem__(self, item: bytes) -> bytes:
        for key in self._headers:
            if key.lower() == item.lower():
                return self._headers[key]
        raise KeyError("{}".format(item))

    def __delitem__(self, key: bytes) -> None:
        for k in self._headers.keys():
            if k.lower() == key.lower():
                del self._headers[k]
                break

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

    def to_bytes(self) -> bytes:
        """
        Converts the headers to bytes to be sent.
        :return: The headers as bytes.
        """
        return b'\r\n'.join([b'%b: %b' % (name, value) for name, value in self._headers.items()] + [b''])


class HTTPMessage:
    def __init__(self):
        self.headers = None
        self.cookies = None
        self.url = None
        self.method = None
        self.body = b''
        self.version = b''
        self.url_bytes = b''

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
            self.url_bytes = url
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
        _cookies = []
        for name, value in self._header_buffer:
            if name is not None:
                if _buf_done or _buf is None:
                    if _buf == b'Cookie':
                        _cookies.append(_headers[b'Cookie'])
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

        if _buf == b'Cookie':
            _cookies.append(_headers[b'Cookie'])
            del _headers[b'Cookie']

        self.headers = HTTPHeaders(_headers)
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


class HTTPRequest(HTTPMessage):
    def __init__(self):
        HTTPMessage.__init__(self)

    def to_bytes(self) -> bytes:
        """
        Converts the HTTPRequest to bytes.
        :return: Bytes received.
        """
        return b'%b %b HTTP/%b\r\n%b%b\r\n%b' % (
            self.method, self.url_bytes, self.version, self.headers.to_bytes(), self.cookies.to_bytes(), self.body
        )


class HTTPResponse(HTTPMessage):
    def __init__(self):
        HTTPMessage.__init__(self)
        self.status_code = 200
        self.headers = HTTPHeaders({})

    def __setattr__(self, key: str, value) -> None:
        if key == "status_code":
            if not isinstance(value, int) or value not in stormsurge.http.status.STATUS_CODES:
                raise ValueError("{} is not a valid HTTP status code.".format(repr(value)))
        super(HTTPMessage, self).__setattr__(key, value)

    def to_bytes(self) -> bytes:
        """
        Converts the HTTPResponse to bytes.
        :return: Bytes to send.
        """
        return b'HTTP/%b %d %b\r\n%b%b\r\n%b' % (
            self.version, self.status_code, stormsurge.http.status.STATUS_CODES[self.status_code],
            self.headers.to_bytes(), self.cookies.to_bytes(set_cookies=True), self.body
        )


def _sort_options_by_qvalue(header: bytes) -> typing.List[bytes]:
    """
    Pulls apart a header value if it's a list and
    sort the values in the list by their qvalue.
    Note: This function parses but ignores level=# attributes
    as they are deprecated and rarely used.
    :param header: Header value to parse.
    :return: List of options sorted by their qvalue.
    """
    qvalues = [_QVALUE_REGEX.match(val).groups() for val in header.split(b',')]
    values = [(float(qval if qval is not None else 1.0), value) for value, qval in qvalues]
    return [value for _, value in sorted(values, reverse=True)]


async def receive_client(loop: asyncio.AbstractEventLoop, client: socket.socket) -> None:
    """
    Function that receives and waits for a client to send requests.
    :param loop: Event loop to add tasks to.
    :param client: Client socket to read request from.
    :return: None
    """
    try:
        client.setblocking(False)
        client.setsockopt(socket.IPPROTO_IP, socket.TCP_NODELAY, 1)
    except (OSError, NameError):
        pass

    while True:
        http_request = HTTPRequest()
        try:
            request_parser = httptools.HttpRequestParser(http_request)
            while not http_request.is_complete():
                try:
                    data = await loop.sock_recv(client, 102400)
                except OSError:
                    return
                if len(data) > 0:
                    request_parser.feed_data(data)
                else:
                    return

            http_request.method = request_parser.get_method()
            http_request.version = request_parser.get_http_version().encode("latin-1")

            if http_request.url is None:
                return
        except httptools.HttpParserError:
            return

        loop.create_task(process_request(loop, client, http_request))


async def process_request(loop: asyncio.AbstractEventLoop, client: socket.socket, http_request: HTTPRequest) -> None:
    """
    Processes a single HTTPRequest object and returns a response.
    :param loop: Event loop to add tasks to.
    :param client: Client socket to write the response to.
    :param http_request: HTTPRequest to process.
    :return: None
    """
    http_response = HTTPResponse()  #TODO: Figure out HTTPResponse here.

    should_close = http_request.headers.get(b'Connection', b'') != b'keep-alive'
    if should_close:
        http_response.headers[b'Connection'] = b'close'

    try:
        await loop.sock_sendall(client, http_response.to_bytes())
        if should_close:
            client.close()
    except OSError:
        pass

