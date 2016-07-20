import asyncio
import httptools
import socket
import ssl
import typing
from .router import *
from ._http import *

# Global Variables
__all__ = [
    "Application"
]


class Application:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.router = Router(self.loop)

    def make_handler(self):
        """
        Creates a handler for an asyncio server.
        :return:
        """
        return lambda: RequestHandler(self, self.router)


class RequestHandler(asyncio.Protocol):
    def __init__(self, app: Application, router: Router):
        self._app = app
        self._router = router
        self._loop = app.loop
        self._socket = None
        self._queue = asyncio.Queue(loop=self._loop)

    def connection_made(self, transport: asyncio.Transport) -> None:
        self._socket = transport.get_extra_info("socket")
        asyncio.ensure_future(self.handle_client(self._socket), loop=self._loop)

    def data_received(self, data: bytes):
        self._queue.put_nowait(data)

    def connection_lost(self, exc):
        try:
            if self._socket is not None:
                self._socket.close()
        except OSError:
            pass

    async def handle_client(self, client: socket.socket) -> None:
        """
        Function that receives and waits for a client to send requests.
        :param client: Client socket to read request from.
        :return: None
        """
        try:
            client.setblocking(False)
            client.setsockopt(socket.IPPROTO_IP, socket.TCP_NODELAY, 1)
        except (OSError, NameError):
            pass
        try:
            while True:
                request = HTTPRequest()
                try:
                    request_parser = httptools.HttpRequestParser(request)
                    while not request.is_complete():
                        data = await self._queue.get()
                        if len(data) > 0:
                            request_parser.feed_data(data)
                        else:
                            client.close()
                            return
                    request.method = request_parser.get_method()
                    request.version = request_parser.get_http_version().encode("latin-1")
                    if request.url is None:
                        client.close()
                        return
                except httptools.HttpParserError:
                    client.close()
                    return
                await self._router.process_request(client, request)
        except OSError:
            return


def run_app(app: Application, host: str="0.0.0.0", port: int=8080, ssl_context: typing.Optional[ssl.SSLContext]=None) -> None:
    """
    Runs an Application object as an asyncio server.
    :param app: Application to run.
    :param host: Host address to bind to.
    :param port: Port to bind to.
    :param ssl_context: Optional SSLContext object.
    :return: None
    """
    scheme = "http"
    if ssl_context is not None:
        scheme = "https"

    print("======== Running on {}://{}:{}/ ========".format(scheme, host, port))
    print("(Press CTRL+C to quit)")

    loop = app.loop
    server = loop.run_until_complete(loop.create_server(
        app.make_handler(), host, port,
        ssl=ssl_context, backlog=512, reuse_address=True
    ))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())