import re

# Global Variables
__all__ = [
    "HttpUrl"
]
_QUERY_REGEX = re.compile(b'([^=&]+)=([^=&]+)')


class HttpUrl:
    def __init__(self, raw: bytes, schema: bytes, host: bytes, port: int, path: bytes,
                 query: bytes, fragment: bytes, user_info: bytes):
        self.raw = raw
        self.schema = schema if schema is not None else b''
        self.host = host if host is not None else b''
        self.port = port if port is not None else -1
        self.path = path if (path is not None and path != b'') else b'/'
        self.query = {key: val for key, val in _QUERY_REGEX.findall(b'' if query is None else query)}
        self.fragment = fragment if fragment is not None else b''
        self.user_info = user_info if user_info is not None else b''
        self._get_form = self.path + ((b'?' + query) if query else b'')

    def get(self) -> bytes:
        return self._get_form

    def __repr__(self):
        return "<HttpUrl raw={}>".format(self.raw)
