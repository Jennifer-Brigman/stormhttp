import httptools
from .message import HttpMessage
from .url import HttpURL

# Global Variables
__all__ = [
    "HttpRequest"
]


class HttpRequest(HttpMessage):
    def __init__(self):
        HttpMessage.__init__(self)
        self.url = None
        self.method = b''

    def on_url(self, raw_url: bytes):
        if raw_url != b'':
            url = httptools.parse_url(raw_url)
            self.url = HttpURL(raw_url, url.schema, url.host, url.port, url.path, url.query, url.fragment, url.userinfo)

    def to_bytes(self) -> bytes:
        parts = [b'%b %b HTTP/%b' % (self.method, self.url.raw, self.version)]
        if len(self.headers) > 0:
            parts.append(self.headers.to_bytes())
        if len(self.cookies) > 0:
            parts.append(self.cookies.to_bytes())
        parts.append(b'')
        parts.append(self.body)
        return b'\r\n'.join(parts)
