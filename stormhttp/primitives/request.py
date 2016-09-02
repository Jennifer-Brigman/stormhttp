import httptools
import typing
from .message import HttpMessage
from .url import HttpUrl

# Global Variables
__all__ = [
    "HttpRequest"
]
_HTTP_REQUEST_FORMAT_STRING = b'%b %b HTTP/%b'


class HttpRequest(HttpMessage):
    def __init__(self, headers: typing.Dict[bytes, typing.Union[bytes, typing.Iterable[bytes]]]=None):
        HttpMessage.__init__(self)
        if headers is not None:
            for key, val in headers:
                self.headers[key] = val
        self.url = None
        self.method = b''

    def on_url(self, raw_url: bytes):
        if raw_url != b'':
            url = httptools.parse_url(raw_url)
            self.url = HttpUrl(raw_url, url.schema, url.host, url.port, url.path, url.query, url.fragment, url.userinfo)

    def to_bytes(self) -> bytes:
        parts = [_HTTP_REQUEST_FORMAT_STRING % (self.method, self.url.get(), self.version)]
        if len(self.headers) > 0:
            parts.append(self.headers.to_bytes())
        if len(self.cookies) > 0:
            parts.append(self.cookies.to_bytes())
        parts.append(b'')
        parts.append(self.body)
        return b'\r\n'.join(parts)

    def __repr__(self):
        return "<HttpRequest version={} method={} url={} headers={}>".format(self.version, self.method, self.url, self.headers)
