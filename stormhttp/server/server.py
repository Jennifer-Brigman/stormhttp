import asyncio
import ssl as _ssl
import typing
from .router import RequestRouter
from ..primitives import HttpParser, HttpRequest, HttpResponse

__all__ = [
    "ServerHttpProtocol",
    "Server"
]


class ServerHttpProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server  # type: Server
        self.transport = None
        self._request = HttpRequest()
        self._parser = HttpParser(self._request)

    def connection_made(self, transport: asyncio.Transport):
        self.transport = transport

    def data_received(self, data: bytes):
        if self._request is None:
            new_request = HttpRequest()
            self._request = new_request
            self._parser.set_target(new_request)

        self._parser.feed_data(data)

        if self._request.is_complete():
            self.server.loop.create_task(self.server.router.route_request(self._request, self.transport))
            self._request = None


class Server:
    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop]=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self._coro = None
        self.router = RequestRouter()

    def run(self, host: str, port: int, ssl: _ssl.SSLContext=None):
        try:
            self.loop.run_until_complete(self.loop.create_server(lambda: ServerHttpProtocol(self), host, port, ssl=ssl))
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
