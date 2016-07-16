import asyncio
import datetime
import hashlib
import os
import typing
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


class FileEndPoint(AbstractEndPoint):
    def __init__(self, path: str, content_type: typing.Optional[bytes]=None):
        AbstractEndPoint.__init__(self)
        self._path = path
        self._etag = None
        self._mtime = None
        self._last_mod = None
        self._cache = None
        self._content_type = content_type
        if content_type is None and "." in os.path.basename(path):
            ext = path[path.rfind("."):]
            if ext in EXTENSION_TO_MIMETYPE:
                self._content_type = EXTENSION_TO_MIMETYPE[ext]
        if self._content_type is None:
            self._content_type = b"text/plain"

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
        self._last_mod = datetime.datetime.utcfromtimestamp(mtime).strftime(HTTP_DATETIME_FORMAT).encode("latin-1")
        with open(self._path, "rb") as f:
            payload = f.read()
            self._cache = payload
            self._etag = hashlib.sha1(payload).digest()
            return payload

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: HTTPRequest) -> HTTPResponse:
        response = HTTPResponse()
        response.version = request.version

        resend_data = True
        if b'If-None-Match' in request.headers and self._etag == request.headers[b'If-None-Match']:
            resend_data = False
        if not resend_data and b'If-Modified-Since' in request.headers:
            try:
                modified_since = datetime.datetime.strptime(
                    request.headers[b'If-Modified-Since'].decode("latin-1"), HTTP_DATETIME_FORMAT
                )
                if modified_since <= self._last_mod:
                    resend_data = False
            except (UnicodeDecodeError, ValueError):
                pass

        if resend_data:
            try:
                modified = await loop.run_in_executor(None, self._file_modified)
                response.body = modified
                response.headers[b'Content-Length'] = b'%d' % (len(modified),)
                response.headers[b'ETag'] = self._etag
                response.headers[b'Last-Modified'] = self._last_mod
                return response
            except OSError:
                response.status_code = 404
                return response
        else:
            response.status_code = 304
            return response
