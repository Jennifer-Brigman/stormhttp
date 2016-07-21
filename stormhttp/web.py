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


class Application(dict):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        dict.__init__(self)
        self.loop = loop
        self.router = Router(self.loop)

    async def listen_to_client(self, client: socket.socket) -> None:
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
                request.app = self
                try:
                    request_parser = httptools.HttpRequestParser(request)
                    while not request.is_complete():
                        try:
                            data = await self.loop.sock_recv(client, 102400)
                        except OSError:
                            client.close()
                            return
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
                await self.router.process_request(client, request)
        except OSError:
            return


def run_app(app: Application, host: str="0.0.0.0", port: int=5000, ssl_context: typing.Optional[ssl.SSLContext]=None, **kwargs) -> None:
    """
    Runs an Application object as an asyncio server.
    :param app: Application to run.
    :param host: Host address to bind to.
    :param port: Port to bind to.
    :param ssl_context: Optional SSLContext object.
    :return: None
    """
    async def _connect_loop(_loop: asyncio.AbstractEventLoop) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        try:  # Try to reuse the address, not available on all systems.
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        except (NameError, OSError):
            pass

        server.bind((host, port))
        server.listen(kwargs.get("backlog", 512))
        while True:
            client, _ = await _loop.sock_accept(server)
            _loop.create_task(app.listen_to_client(client))

    scheme = "http"
    if ssl_context is not None:
        scheme = "https"
    print("======== Running on {}://{}:{}/ ========".format(scheme, host, port))
    print("(Press CTRL+C to quit)")

    loop = app.loop
    loop.run_until_complete(_connect_loop(loop))
    loop.run_forever()
