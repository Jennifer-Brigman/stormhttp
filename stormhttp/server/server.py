import asyncio
import ssl as _ssl
import typing
from ..primitives import HttpParser, HttpRequest, HttpResponse

__all__ = [
    "ServerHttpProtocol",
    "Server"
]


class ServerHttpProtocol(asyncio.Protocol):
    def __init__(self):
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
            self._request = None


class Server:
    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop]=None):
        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._coro = None

    async def run(self, host: str, port: int, ssl: _ssl.SSLContext=None):
        self._coro = self._loop.create_server(ServerHttpProtocol, host, port, ssl=ssl)
        await self._coro