import asyncio
import typing
from ..primitives import HttpRequest, HttpResponse
from ..primitives.message import _SUPPORTED_ENCODINGS

__all__ = [
    "RequestRouter"
]
_PREFIX_DELIMITER = b'/'
_PREFIX_LEAF = b'/'
_HEADER_ACCEPT_ENCODING = b'Accept-Encoding'


class RequestRouter:
    def __init__(self):
        self._prefix = {}  # type: typing.Dict[bytes, typing.Any]
        self.min_compression_length = 1400

    def add_route(self, path: bytes, method: bytes, handler: typing.Callable[[HttpRequest], HttpResponse]) -> None:
        prefix_branch = self._traverse_prefix_autofill(path)
        if _PREFIX_LEAF in prefix_branch:
            if method in prefix_branch[_PREFIX_LEAF]:
                raise ValueError("Route {} {} already exists.".format(method, path))
            prefix_branch[_PREFIX_LEAF][method] = handler
        else:
            prefix_branch[_PREFIX_LEAF] = {method: handler}

    async def route_request(self, request: HttpRequest, transport: asyncio.WriteTransport):
        prefix_branch = self._traverse_prefix_nofill(request.url.path)
        if prefix_branch is None:
            response = HttpResponse()
            response.status_code = 404
            response.status = b'Not Found'
            response.headers[b'Content-Length'] = 0
        else:
            is_head = False
            if request.method == b'HEAD' and request.method not in prefix_branch and b'GET' in prefix_branch:
                request.method = b'GET'
                is_head = True
            if request.method not in prefix_branch:
                response = HttpResponse()
                response.headers[b'Allow'] = b', '.join(list(prefix_branch.keys()))
                response.status_code = 405
                response.status = b'Method Not Allowed'
                response.headers[b'Content-Length'] = 0
            else:
                handler = prefix_branch[request.method]
                if asyncio.iscoroutinefunction(handler):
                    response = await handler(request)
                else:
                    response = handler(request)
            if is_head:
                response.body = b''
        if b'Accept-Encoding' in request.headers and len(response) > self.min_compression_length:
            for encoding, _ in request.headers.qlist(b'Accept-Encoding'):
                if encoding in _SUPPORTED_ENCODINGS:
                    response.set_encoding(encoding)
                    break
        response.version = request.version
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

    def _traverse_prefix_nofill(self, path: bytes) -> typing.Optional[typing.Dict[bytes, typing.Any]]:
        """
        Traverses the prefix trie and returns the resulting leaf.
        This method does not fill in branches. Returns None if the leaf cannot be found.
        :param path: Path to traverse.
        :return: Leaf node of the prefix trie.
        """
        path = path.strip(b'/').split(b'/')
        current = self._prefix
        for step in path:
            if step == b'':
                continue
            if step not in current:
                return None
            current = current[step]
        return current.get(_PREFIX_LEAF, None)
