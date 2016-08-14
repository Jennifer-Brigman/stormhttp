import re
import typing
from .headers import HttpHeaders
from .cookies import HttpCookies

# Global Variables
__all__ = [
    "HttpMessage"
]
_COOKIE_REGEX = re.compile(b'([^\\s=;]+)(?:=([^=;]+))?(?:;|$)')


class HttpMessage:
    def __init__(self):
        self.headers = HttpHeaders()
        self.cookies = HttpCookies()
        self.body = b''
        self.version = b''

        self._body_buffer = []
        self._header_buffer = []
        self._is_header_complete = False
        self._is_complete = False

    def is_complete(self) -> bool:
        return self._is_complete

    def is_header_complete(self) -> bool:
        return self._is_header_complete

    def to_bytes(self) -> bytes:
        raise NotImplementedError("HttpMessage.to_bytes() is not implemented.")

    # httptools parser interface

    def on_header(self, key: typing.Optional[bytes], val: typing.Optional[bytes]):
        self._header_buffer.append((key, val))

    def on_headers_complete(self) -> None:
        _headers = {}
        _key_buffer = []
        _val_buffer = []
        _key = None

        for key, val in self._header_buffer:
            if key is not None:
                if _key_buffer is None:
                    _key_buffer = [key]
                    if _key is not None:
                        _headers[_key] = b''.join(_val_buffer)
                    _key = None
                else:
                    _key_buffer.append(key)
            if val is not None:
                if _key is None:
                    _key = b''.join(_key_buffer)
                    _key_buffer = None
                    _val_buffer = []
                _val_buffer.append(val)
        if _key is not None:
            _headers[_key] = b''.join(_val_buffer)

        self.headers.update(_headers)
        print(self.headers)
        if b'Cookie' in self.headers:
            try:
                print(self.headers[b'Cookie'])
                self.cookies.update({key: val for key, val in _COOKIE_REGEX.findall(self.headers[b'Cookie'])})
                del self.headers[b'Cookie']
            except Exception as err:
                print(str(type(err)))
                print(str(err))
        print(self.headers)

        self._is_header_complete = True

    def on_body(self, body: bytes) -> None:
        self._body_buffer.append(body)

    def on_message_complete(self) -> None:
        self.body = b''.join(self._body_buffer)
        self._is_complete = True
