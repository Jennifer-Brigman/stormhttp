import os
from ._http import *
from ._endpoints import *

__all__ = [
    "AbstractMountable",
    "VirtualDirectoryMount"
]


class AbstractMountable:
    def __init__(self):
        self.prefix = ""

    async def on_request(self, request: HTTPRequest) -> HTTPResponse:
        raise NotImplementedError("AbstractMountable.on_request() is not implemented.")

    def get_mounted_path(self, url: str) -> str:
        if url.startswith(self.prefix):
            url = url[len(self.prefix):]
        return url


class VirtualDirectoryMount(AbstractMountable):
    def __init__(self, directory: str):
        AbstractMountable.__init__(self)
        self._directory = os.path.realpath(directory)
        self._endpoints = {}

    async def on_request(self, request: HTTPRequest) -> HTTPResponse:
        route = self.get_mounted_path(request.url_bytes)
        virtual_path = os.path.join(self._directory, route.strip("/"))

        if not self._is_sub_path(virtual_path):
            return request.decorate_response(HTTPErrorResponse(403))

        if request.method not in ["GET", "HEAD"]:
            response = request.decorate_response(HTTPErrorResponse(405))
            response.headers["Allow"] = "GET,HEAD"
            return response

        if os.path.isdir(virtual_path):
            virtual_path = os.path.join(virtual_path, "index.html")

        if virtual_path not in self._endpoints:
            self._endpoints[virtual_path] = FileEndpoint(virtual_path)

        return await self._endpoints[virtual_path].on_request(request.app.loop, request)

    def _is_sub_path(self, sub_path: str) -> bool:
        rel_path = os.path.relpath(os.path.realpath(sub_path), self._directory)
        return rel_path != os.pardir and not rel_path.startswith(os.pardir + os.sep)
