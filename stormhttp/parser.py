import typing
import httptools
from .message import HttpMessage
from .request import HttpRequest
from .response import HttpResponse

# Global Variables
__all__ = [
    "HttpParser"
]


class HttpParser:
    def __init__(self, message: typing.Optional[HttpMessage]=None):
        self._message = None
        self._parser = None
        if message is not None:
            self.set_target(message)

    def set_target(self, message: HttpMessage):
        if isinstance(message, HttpRequest):
            self._parser = httptools.HttpRequestParser(message)
        else:
            self._parser = httptools.HttpResponseParser(message)
        self._message = message

    def feed_data(self, data: bytes):
        self._parser.feed_data(data)
        if self._message.is_header_complete():
            if isinstance(self._message, HttpRequest):
                self._message.method = self._parser.get_method()
            elif isinstance(self._message, HttpResponse):
                self._message.status_code = self._parser.get_status_code()
            self._message.version = self._parser.get_http_version().encode("ascii")

