import typing
import httptools
from .message import HttpMessage
from .request import HttpRequest
from .response import HttpResponse

# Global Variables
__all__ = [
    "HttpParser",
    "HttpParserError"
]


class HttpParserError(Exception):
    pass


class HttpParser:
    def __init__(self, message: typing.Optional[HttpMessage]=None):
        self._message = None
        self._parser = None
        self._headers_done = False
        if message is not None:
            self.set_target(message)

    def set_target(self, message: HttpMessage):
        """
        Sets the HttpMessage for the data to be parsed into.
        :param message: HttpRequest or HttpResponse to
        :return:
        """
        if isinstance(message, HttpRequest):
            self._parser = httptools.HttpRequestParser(message)
        elif isinstance(message, HttpResponse):
            self._parser = httptools.HttpResponseParser(message)
        else:
            raise HttpParserError("Must be called with either HttpRequest or HttpResponse object.")
        self._message = message
        self._headers_done = False

    def feed_data(self, data: bytes):
        """
        Feed byte data into the parser.
        :param data: Data to be parsed.
        :return: None
        """
        try:
            self._parser.feed_data(data)
        except httptools.HttpParserError as error:
            raise HttpParserError(str(error))
        if not self._headers_done and self._message.is_header_complete():
            self._headers_done = True
            if isinstance(self._message, HttpRequest):
                self._message.method = self._parser.get_method()
            else:
                self._message.status_code = self._parser.get_status_code()
            self._message.version = self._parser.get_http_version().encode("ascii")
