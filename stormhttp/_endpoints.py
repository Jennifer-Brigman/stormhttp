import asyncio
import datetime
import hashlib
import os
import typing
import types
from ._constants import HTTP_DATETIME_FORMAT
from ._http import *
from ._mimetype import EXTENSION_TO_MIMETYPE

# Global Variables
__all__ = [
    "AbstractEndPoint",
    "FileEndPoint"
]


class AbstractEndPoint:
    async def on_request(self, loop: asyncio.AbstractEventLoop, request: HTTPRequest) -> HTTPResponse:
        raise NotImplementedError("AbstractEndPoint.on_request is not implemented.")


class ConstantEndPoint(AbstractEndPoint):
    def __init__(self, payload: bytes, content_type: bytes=b'text/html', content_charset: bytes=b'utf-8'):
        AbstractEndPoint.__init__(self)
        self._payload = payload
        self._content_type = b'%b; charset=%b' % (content_type, content_charset)

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: HTTPRequest) -> HTTPResponse:
        response = HTTPResponse()
        response.cookies = request.cookies
        response.body = self._payload
        response.headers[b'Content-Type'] = self._content_type
        return response


class EndPoint(AbstractEndPoint):
    def __init__(self, handler: typing.Callable[[HTTPRequest], typing.Union[types.CoroutineType, HTTPResponse]],
                 content_type: bytes=b'text/html', content_charset: bytes=b'utf-8', cache_length: int=0):
        AbstractEndPoint.__init__(self)
        self._handler = handler
        self._content_type = b'%b; charset=%b' % (content_type, content_charset)

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: HTTPRequest) -> HTTPResponse:
        if asyncio.iscoroutinefunction(self._handler):
            response = await self._handler(request)
        else:
            response = self._handler(request)

        response.headers[b'Content-Type'] = self._content_type
        return response


class FileEndPoint(AbstractEndPoint):
    def __init__(self, path: str, content_type: typing.Optional[bytes]=None, encoding: str="utf-8"):
        AbstractEndPoint.__init__(self)
        self._path = path
        self._etag = None
        self._mtime = None
        self._last_mod = None
        self._last_mod_dt = None
        self._cache = None
        self._content_type = content_type
        self._encoding = encoding
        if content_type is None and "." in os.path.basename(path):
            ext = path[path.rfind("."):]
            if ext in EXTENSION_TO_MIMETYPE:
                self._content_type = EXTENSION_TO_MIMETYPE[ext][0]
        if self._content_type is None:
            self._content_type = b'text/plain'
        self._content_type += b'; charset=%b' % (self._encoding.encode("latin-1"),)

    def _file_modified(self) -> bool:
        """
        Checks to see if the file is modified
        and if it has been changed by it's modify-time.
        :return: None
        """
        mtime = int(os.stat(self._path).st_mtime)
        if self._cache is not None and mtime <= self._mtime:
            return self._cache
        self._mtime = mtime
        self._last_mod_dt = datetime.datetime.utcfromtimestamp(mtime)
        self._last_mod = self._last_mod_dt.strftime(HTTP_DATETIME_FORMAT).encode("latin-1")
        with open(self._path, "rb") as f:
            payload = f.read()
            self._cache = payload
            self._etag = hashlib.sha1(payload).hexdigest().encode("latin-1")
            return payload

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: HTTPRequest) -> HTTPResponse:
        response = HTTPResponse()
        response.version = request.version

        resend_data = True
        if b'If-Modified-Since' in request.headers and self._last_mod_dt is not None:
            try:
                modified_since = datetime.datetime.strptime(
                    request.headers[b'If-Modified-Since'].decode("latin-1"),
                    HTTP_DATETIME_FORMAT
                )
                if modified_since >= self._last_mod_dt:
                    resend_data = False
            except (UnicodeDecodeError, ValueError) as error:
                pass

        if resend_data:
            try:
                modified = await loop.run_in_executor(None, self._file_modified)
                if b'If-None-Match' in request.headers and self._etag == request.headers[b'If-None-Match']:
                    response.status_code = 304
                    return response
                response.body = modified
                response.headers[b'Content-Length'] = b'%d' % (len(modified),)
                response.headers[b'Content-Type'] = self._content_type
                response.headers[b'ETag'] = self._etag
                response.headers[b'Last-Modified'] = self._last_mod
                return response
            except OSError:
                response.status_code = 404
                return response
        else:
            response.status_code = 304
            return response
