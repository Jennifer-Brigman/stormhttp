import brotli
import cchardet
import datetime
import gzip
import json
import io
import re
import sys
import typing
import zlib
from .headers import HttpHeaders
from .cookies import HttpCookies, HttpCookie, _COOKIE_EXPIRE_FORMAT

__all__ = [
    "HttpMessage"
]
_COOKIE_REGEX = re.compile(b'([^\\s=;]+)(?:=([^;]+))?(?:;|$)')
_CHARSET_REGEX = re.compile(b'[^/]+/[^/]+;\s*charset=([^=;]+)')
_COOKIE_META = {b'domain', b'path', b'expires', b'maxage', b'httponly', b'secure'}
_SUPPORTED_ENCODINGS = {b'gzip', b'deflate', b'br', b'identity'}
_ENCODING_GZIP = b'gzip'
_ENCODING_DEFLATE = b'deflate'
_ENCODING_BROTLI = b'br'
_ENCODING_IDENTITY = b'identity'
_HEADER_CONTENT_LENGTH = b'Content-Length'
_HEADER_CONTENT_ENCODING = b'Content-Encoding'
_HEADER_CONTENT_TYPE = b'Content-Type'
_HEADER_COOKIE = b'Cookie'
_HEADER_SET_COOKIE = b'Set-Cookie'
_HEADER_DEFAULT_CONTENT_ENCODING = [_ENCODING_IDENTITY]


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

    def __len__(self):
        return len(self.body)

    def is_complete(self) -> bool:
        return self._is_complete

    def is_header_complete(self) -> bool:
        return self._is_header_complete

    def to_bytes(self) -> bytes:
        raise NotImplementedError("HttpMessage.to_bytes() is not implemented.")

    def set_encoding(self, encoding: bytes, set_headers: bool=True) -> None:
        """
        Sets the encoding of the body to be a certain Content-Encoding.
        Currently the only supported encodings are identity, gzip, delfate, and brotli.
        :param encoding: Encoding to set the body to be.
        :param set_headers: If True, modifies the headers to reflect the change.
        :return: None
        """
        assert encoding in _SUPPORTED_ENCODINGS
        current_encoding = self.headers.get(_HEADER_CONTENT_ENCODING, _HEADER_DEFAULT_CONTENT_ENCODING)[0]
        if current_encoding == encoding or len(self.body) == 0:
            return  # No-op if the encoding is already correct.

        # Decoding the current encoding.
        if current_encoding != _ENCODING_IDENTITY:
            if current_encoding == _ENCODING_BROTLI:
                self.body = brotli.decompress(self.body)
            elif current_encoding == _ENCODING_GZIP:
                self.body = gzip.GzipFile(fileobj=io.BytesIO(self.body), mode="rb").read()
            elif current_encoding == _ENCODING_DEFLATE:
                self.body = zlib.decompress(self.body, -zlib.MAX_WBITS)

        # Re-encoding with the desired encoding.
        if encoding != _ENCODING_IDENTITY:
            if encoding == _ENCODING_BROTLI:
                self.body = brotli.compress(self.body)
            elif encoding == _ENCODING_GZIP:
                out = io.BytesIO()
                gzip.GzipFile(fileobj=out, mode="wb").write(self.body)
                self.body = out.getvalue()
            elif encoding == _ENCODING_DEFLATE:
                deflate = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
                self.body = deflate.compress(self.body) + deflate.flush()

        # Optionally set the headers.
        if set_headers:
            self.headers[_HEADER_CONTENT_LENGTH] = b'%d' % len(self.body)
            self.headers[_HEADER_CONTENT_ENCODING] = encoding

    def body_string(self) -> str:
        """
        Decodes the body of the HTTP message as a string
        while attempting to decode the body. If the body is
        not in an 'identity' character encoding, does the decoding
        and puts the body back into the encoding.
        :return: Body decoded as a string.
        """
        # If the body is encoded or compressed, need to decompress it before getting the string.
        encoding = self.headers.get(_HEADER_CONTENT_ENCODING, _HEADER_DEFAULT_CONTENT_ENCODING)[0]
        if encoding != _ENCODING_IDENTITY:
            self.set_encoding(_ENCODING_IDENTITY, set_headers=False)
        body = None

        # If the headers are giving us a hint, then try them first.
        charset = _CHARSET_REGEX.match(self.headers.get(_HEADER_CONTENT_TYPE, [b''])[0])
        if charset is not None:
            charset = charset.group(1).decode("utf-8")
            try:
                body = self.body.decode(charset)
            except UnicodeDecodeError:
                pass

        # Otherwise try the system default encoding followed by cchardet attempting to detect encoding.
        if body is None:
            try:
                body = self.body.decode(sys.getdefaultencoding())
            except UnicodeDecodeError:
                body = self.body.decode(cchardet.detect(self.body)["encoding"])

        # Revert back to the old encoding.
        if encoding != _ENCODING_IDENTITY:
            self.set_encoding(encoding, set_headers=False)

        return body

    def body_json(self, loads=json.loads) -> typing.Union[dict, list]:
        """
        Loads the body as a JSON object if it is valid JSON.
        :param loads: Function to load the body as JSON with. Default: json.loads
        :return: The body as JSON.
        """
        return loads(self.body_string())

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
                        _headers[_key] = _headers.get(_key, []) + [b''.join(_val_buffer)]
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
            _headers[_key] = _headers.get(_key, []) + [b''.join(_val_buffer)]

        self.headers.update(_headers)
        if _HEADER_COOKIE in self.headers:
            for cookie_header in self.headers[_HEADER_COOKIE]:
                cookie = HttpCookie()
                for key, value in _COOKIE_REGEX.findall(cookie_header):
                    cookie.values[key] = value
                self.cookies.add(cookie)
            del self.headers[_HEADER_COOKIE]

        if _HEADER_SET_COOKIE in self.headers:
            for cookie_header in self.headers[_HEADER_SET_COOKIE]:
                cookie = HttpCookie()
                for key, value in _COOKIE_REGEX.findall(cookie_header):
                    key_lower = key.lower()
                    if key_lower in _COOKIE_META:
                        if key_lower == b'secure':
                            cookie.secure = True
                        elif key_lower == b'httponly':
                            cookie.http_only = True
                        elif key_lower == b'domain':
                            cookie.domain = value
                        elif key_lower == b'path':
                            cookie.path = value
                        elif key_lower == b'expires':
                            try:
                                cookie.expires = datetime.datetime.strptime(value.decode("utf-8"), _COOKIE_EXPIRE_FORMAT)
                            except ValueError:
                                pass
                        elif key_lower == b'maxage':
                            try:
                                cookie.max_age = int(value.decode("utf-8"))
                            except ValueError:
                                pass
                            except UnicodeDecodeError:
                                pass
                    else:
                        cookie.values[key] = value
                self.cookies.add(cookie)
            del self.headers[_HEADER_SET_COOKIE]

        self._is_header_complete = True

    def on_body(self, body: bytes) -> None:
        self._body_buffer.append(body)

    def on_message_complete(self) -> None:
        self.body = b''.join(self._body_buffer)
        self._is_complete = True
