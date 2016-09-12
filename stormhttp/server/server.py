import asyncio
import datetime
import re
import ssl as _ssl
import typing
from .middleware import AbstractMiddleware
from ..primitives import HttpParser, HttpRequest, HttpResponse
from ..primitives.message import _SUPPORTED_ENCODINGS

__all__ = [
    "ServerHttpProtocol",
    "Server"
]
_MATCH_INFO_REGEX = re.compile(b'^<([a-zA-Z_][a-zA-Z0-9_]*)>$')


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
            self.server.loop.create_task(self.server.route_request(self._request, self.transport))
            self._request = None


class Server:
    def __init__(self, loop: typing.Optional[asyncio.AbstractEventLoop]=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self._prefix = {}  # type: typing.Dict[bytes, typing.Any]
        self.middlewares = []  # type: typing.List[AbstractMiddleware]
        self.min_compression_length = 1400

        from .. import __version__
        self.server_version = __version__
        self.server_header = b'Stormhttp/' + __version__.encode("utf-8")

    def run(self, host: str, port: int=None, ssl: _ssl.SSLContext=None):
        if port is None:
            if ssl is None:
                port = 8080
            else:
                port = 8443
        print("===== Running on {}://{}:{}/ (Stormhttp/{})=====\n(Press Ctrl+C to quit)".format(
            "http" if ssl is None else "https",
            host, port, self.server_version
        ))
        try:
            self.loop.run_until_complete(self.loop.create_server(lambda: ServerHttpProtocol(self), host, port, ssl=ssl))
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass

    def add_route(self, path: bytes, method: bytes, handler: typing.Callable[[HttpRequest], HttpResponse]) -> None:
        prefix_branch = self._traverse_prefix_autofill(path)
        if b'/' in prefix_branch:
            if method in prefix_branch[b'/']:
                raise ValueError("Route {} {} already exists.".format(method, path))
            prefix_branch[b'/'][method] = handler
        else:
            prefix_branch[b'/'] = {method: handler}

    async def route_request(self, request: HttpRequest, transport: asyncio.WriteTransport):
        prefix_branch = self._traverse_prefix_nofill(request)
        if prefix_branch is None:
            response = HttpResponse(status_code=404, status=b'Not Found')
        else:
            is_head = False
            if request.method == b'HEAD' and request.method not in prefix_branch and b'GET' in prefix_branch:
                request.method = b'GET'
                is_head = True
            if request.method not in prefix_branch:
                response = HttpResponse(status_code=405, status=b'Method Not Allowed')
                response.headers[b'Allow'] = b', '.join(list(prefix_branch.keys()))
            else:

                # If the correct request handler is found, begin applying middlewares.
                response = None
                applied_middleware = []
                for middleware in self.middlewares:
                    if middleware.should_be_applied(request):
                        if asyncio.iscoroutinefunction(middleware.before_handler):
                            response = await middleware.before_handler(request)
                        else:
                            response = middleware.before_handler(request)
                        if response is not None:
                            break
                        applied_middleware.append(middleware)

                # If we haven't gotten a response yet, do the handler.
                if response is None:
                    handler = prefix_branch[request.method]
                    if asyncio.iscoroutinefunction(handler):
                        response = await handler(request)
                    else:
                        response = handler(request)

                # Apply middlewares after_handler() in reverse order.
                # This is mostly for AbstractTemplatingMiddlewares to work correctly.
                for middleware in applied_middleware[::-1]:
                    if asyncio.iscoroutinefunction(middleware.after_handler):
                        await middleware.after_handler(request, response)
                    else:
                        middleware.after_handler(request, response)

            if is_head:
                response.body = b''

        # Apply headers to the response that are always applied.
        response.version = request.version
        if b'Accept-Encoding' in request.headers and len(response) > self.min_compression_length:
            for encoding, _ in request.headers.qlist(b'Accept-Encoding'):
                if encoding in _SUPPORTED_ENCODINGS:
                    response.set_encoding(encoding)
                    break
        if b'Content-Length' not in response.headers:
            response.headers[b'Content-Length'] = len(response)
        if b'Date' not in response.headers:
            response.headers[b'Date'] = datetime.datetime.utcnow()
        if b'Server' not in response.headers:
            response.headers[b'Server'] = self.server_header

        transport.write(response.to_bytes())

    def _traverse_prefix_autofill(self, path: bytes) -> typing.Dict[bytes, typing.Any]:
        """
        Traverses the prefix trie and returns the resulting leaf.
        This method also automatically fills in branches where needed to reach the path.
        :param path: Path to traverse.
        :return: Leaf node of the prefix trie.
        """
        path = path.strip(b'/').split(b'/')
        current = self._prefix
        for step in path:
            if step == b'':
                continue
            if step not in current:
                current[step] = {}
            current = current[step]
        return current

    def _traverse_prefix_nofill(self, request: HttpRequest) -> typing.Optional[typing.Dict[bytes, typing.Any]]:
        """
        Traverses the prefix trie and returns the resulting leaf.
        This method does not fill in branches. Returns None if the leaf cannot be found.
        This method also fills the request.match_info values.
        :param request: HttpRequest to traverse the path for and fill in match_info values.
        :return: Leaf node of the prefix trie.
        """
        path = request.url.path.strip(b'/').split(b'/')
        current = self._prefix
        for step in path:
            if step == b'':
                continue
            if step not in current:
                if len(current) == 1:
                    pos_match_info = list(current.keys())[0]
                    match_info = _MATCH_INFO_REGEX.match(pos_match_info)
                    if match_info is not None:
                        request.url.match_info[match_info.group(1)] = step
                        current = current[pos_match_info]
                        continue
                return None
            current = current[step]
        return current.get(b'/', None)
