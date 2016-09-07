import asyncio
import typing
from ..primitives import HttpRequest, HttpResponse

__all__ = [
    "RequestRouter"
]
_PREFIX_DELIMITER = b'/'
_PREFIX_LEAF = b'/'
_HTTP_METHOD_GET = b'GET'
_HTTP_METHOD_HEAD = b'HEAD'


class RequestRouter:
    def __init__(self):
        self._prefix = {}

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
        else:
            is_head = False
            if request.method == _HTTP_METHOD_HEAD and request.method not in prefix_branch and _HTTP_METHOD_GET in prefix_branch:
                request.method = _HTTP_METHOD_GET
                is_head = True
            if request.method not in prefix_branch:
                response = HttpResponse()
                response.headers[b'Allow'] = b', '.join(list(prefix_branch.keys()))
                response.status_code = 405
                response.status = b'Method Not Allowed'
            else:
                handler = prefix_branch[request.method]
                if asyncio.iscoroutinefunction(handler):
                    response = await handler(request)
                else:
                    response = handler(request)
            if is_head:
                response.body = b''
        response.version = request.version
        transport.write(response.to_bytes())

    def _traverse_prefix_autofill(self, path: bytes) -> typing.Dict[bytes, typing.Any]:
        """
        Traverses the prefix trie and returns the resulting leaf.
        This method also automatically fills in branches where needed to reach the path.
        :param path: Path to traverse.
        :return: Leaf node of the prefix trie.
        """
        path = path.strip(_PREFIX_DELIMITER).split(_PREFIX_DELIMITER)
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
        path = path.strip(_PREFIX_DELIMITER).split(_PREFIX_DELIMITER)
        current = self._prefix
        for step in path:
            if step == b'':
                continue
            if step not in current:
                return None
            current = current[step]
        return current.get(_PREFIX_LEAF, None)
