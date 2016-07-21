import asyncio
import re
import socket
import typing
from ._http import *
from ._endpoints import *
from ._compress import *

# Global Variables
__all__ = [
    "Router",
    "AbstractEndPoint",
    "FileEndPoint"
]
_QVALUE_REGEX = re.compile(b'^\\s?([^;]+)\\s?(?:;\\s?q=(\\d\\.\\d)|;\\s?level=\\d+)*$')
_PREFIX_MATCH_REGEX = re.compile(b'^\\{(.+)}$')
_PREFIX_TREE_SENTINEL = b'///'
_PREFIX_TREE_MATCH = b'/*/'


class Router:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._prefix_tree = {}
        self._loop = loop

    def add_endpoint(self, route: bytes, methods: typing.List[bytes], endpoint: AbstractEndPoint) -> None:
        """
        Adds a single EndPoint to the prefix tree, possibly in multiple locations
        if there are multiple methods in the same route. An error is raised if there
        is already an EndPoint object at the same location in the tree.
        :param route: Route within the prefix tree.
        :param methods: List of methods to accept.
        :param endpoint: EndPoint object to add to the tree.
        :return: None
        """
        route_steps = route.split(b'/')[1:]
        current_node = self._prefix_tree

        for step in route_steps:
            if step == b'':
                continue

            prefix_match = _PREFIX_MATCH_REGEX.match(step)
            if prefix_match is not None:
                if _PREFIX_TREE_MATCH in current_node:
                    raise ValueError("Route {} has more than one match point.".format(route))
                current_node[_PREFIX_TREE_MATCH] = prefix_match.groups()[0]
                continue

            if step not in current_node:
                current_node[step] = {}
            current_node = current_node[step]

        if _PREFIX_TREE_SENTINEL not in current_node:
            current_node[_PREFIX_TREE_SENTINEL] = {}
        current_node = current_node[_PREFIX_TREE_SENTINEL]

        for method in methods:
            if method in current_node:
                raise ValueError("Route {} {} has more than one endpoint registered.".format(method, route))
            current_node[method] = endpoint

    async def route_request(self, request: HTTPRequest) -> HTTPResponse:
        """
        Routes an HTTPRequest through the prefix tree to an EndPoint.
        :param request: Request to route to an endpoint.
        :return: HTTPResponse to the request.
        """
        route_steps = request.url.path.split(b'/')[1:]
        current_node = self._prefix_tree
        for step in route_steps:
            if step == b'':
                continue  # This ensures that trailing / also routes to same place.
            if step in current_node:
                current_node = current_node[step]
                continue
            elif _PREFIX_TREE_MATCH in current_node:
                request.match_info[current_node[_PREFIX_TREE_MATCH]] = step
                continue
            return request.decorate_response(HTTPErrorResponse(404))

        if _PREFIX_TREE_SENTINEL in current_node:
            current_node = current_node[_PREFIX_TREE_SENTINEL]
            if request.method in current_node:
                endpoint = current_node[request.method]
                try:
                    return await endpoint.on_request(self._loop, request)
                except Exception:
                    return request.decorate_response(HTTPErrorResponse(500))
            else:
                response = request.decorate_response(HTTPErrorResponse(405))
                response.headers[b'Allow'] = b','.join(current_node)
                return response
        else:
            return request.decorate_response(HTTPErrorResponse(404))

    async def process_request(self, client: socket.socket, request: HTTPRequest) -> None:
        """
        Processes a single HTTPRequest object and returns a response.
        :param client: Client socket to write the response to.
        :param request: HTTPRequest to process.
        :return: None
        """
        response = await self.route_request(request)
        should_close = request.headers.get(b'Connection', b'') != b'keep-alive'

        if should_close:
            response.headers[b'Connection'] = b'close'

        if b'Accept-Encoding' in request.headers and b'Content-Encoding' not in response.headers:
            encodings = self._sort_by_qvalue(request.headers[b'Accept-Encoding'])
            for enc in encodings:
                if enc in SUPPORTED_ENCODING_TYPES:
                    response.body = await self._loop.run_in_executor(None, encode_bytes, enc, response.body)
                    response.headers[b'Content-Encoding'] = enc
                    response.headers[b'Content-Length'] = b'%d' % (len(response.body),)
                    break
        try:
            await self._loop.sock_sendall(client, response.to_bytes())
            if should_close:
                client.close()
        except OSError:
            pass

    @staticmethod
    def _sort_by_qvalue(header: bytes) -> typing.List[bytes]:
        """
        Pulls apart a header value if it's a list and
        sort the values in the list by their qvalue.
        Note: This function parses but ignores level=# attributes
        as they are deprecated and rarely used.
        :param header: Header value to parse.
        :return: List of options sorted by their qvalue.
        """
        qvalues = [_QVALUE_REGEX.match(val).groups() for val in header.split(b',')]
        values = [(float(qval if qval is not None else 1.0), value) for value, qval in qvalues]
        return [value for _, value in sorted(values, reverse=True)]
