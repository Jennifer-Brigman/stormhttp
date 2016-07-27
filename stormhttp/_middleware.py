from ._http import *


class AbstractMiddleware:
    async def on_request(self, request: HTTPRequest):
        raise NotImplementedError("AbstractMiddleware.on_request() is not implemented.")

    async def on_response(self, request: HTTPRequest, response: HTTPResponse):
        raise NotImplementedError("AbstractMiddleware.on_response() is not implemented.")