import re

# Global Variables
__all__ = [
    "HttpURL"
]
_QUERY_REGEX = re.compile(b'([^=&]+=[^=&]+)')


class HttpURL:
    def __init__(self, raw: bytes, schema: bytes, host: bytes, port: int, path: bytes,
                 query: bytes, fragment: bytes, user_info: bytes):
        self.raw = raw
        self.schema = schema
        self.host = host
        self.port = port
        self.path = path
        self.query = {key: val for key, val in _QUERY_REGEX.findall(b'' if query is None else query )}
        self.fragment = fragment
        self.user_info = user_info
