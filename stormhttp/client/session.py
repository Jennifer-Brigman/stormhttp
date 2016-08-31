import asyncio
import cchardet
import httptools
import socket
import ssl as _ssl
import typing
from ..primitives import HttpRequest, HttpResponse, HttpParser, HttpHeaders
from ..errors import SslCertificateVerificationError, SslError

__all__ = [
    "ClientSession"
]
_HTTP_REDIRECTS = {301, 302, 307, 308}
_CERTIFICATE_VERIFY_FAILED = "CERTIFICATE_VERIFY_FAILED"


class ClientSession:
    def __init__(self, loop: asyncio.AbstractEventLoop=None,
                 headers: typing.Dict[bytes, typing.Union[bytes, typing.Iterable[bytes]]]=None,
                 version: bytes=b'1.1'):
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._lock = asyncio.Lock(loop=self._loop)
        self._reader = None  # type: asyncio.StreamReader
        self._writer = None  # type: asyncio.StreamWriter
        self._version = version
        self._host = None
        self._port = None
        self._parser = HttpParser()
        self.headers = HttpHeaders()
        if headers is not None:
            self.headers.update(self.headers)

    def __del__(self):
        if self._writer is not None:
            self._writer.close()
        self._writer = None
        self._reader = None

    async def open(self, address: typing.Tuple[bytes, int], ssl: typing.Optional[_ssl.SSLContext]=None) -> None:
        host, port = address
        if self._reader is None or self._host != host or self._port != port:
            async with self._lock:
                if self._reader is not None:
                    self._writer.close()
                try:
                    self._reader, self._writer = await asyncio.open_connection(
                        host=host.decode(cchardet.detect(host)["encoding"]), port=port,
                        loop=self._loop, ssl=ssl
                    )

                    # Set TCP_NODELAY to allow writes to be minimally buffered.
                    sock = self._writer.transport.get_extra_info("socket")
                    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)

                except _ssl.SSLError as error:
                    if _CERTIFICATE_VERIFY_FAILED in str(error):
                        raise SslCertificateVerificationError("Error occurred while verifying the ceritificate.")
                    else:
                        raise SslError(str(error))
                except _ssl.CertificateError:
                    raise SslCertificateVerificationError("Certificate is invalid or expired.")
                self._host = host
                self._port = port

    async def close(self) -> None:
        async with self._lock:
            if self._reader is not None:
                self._writer.close()
            self._reader = None
            self._writer = None

    async def request(self, url: bytes, method: bytes, headers: typing.Dict[bytes, typing.Union[bytes, typing.Iterable[bytes]]]=None,
                        body: bytes=b'', allow_redirects: bool=True, max_redirects: int=10,
                        buffer_length: int=65536, ssl: _ssl.SSLContext=None) -> HttpResponse:
        parsed_url = httptools.parse_url(url)
        host = parsed_url.host
        schema = parsed_url.schema.lower()
        port = parsed_url.port if parsed_url.port else (
            443 if schema == b'https' else 80
        )
        if ssl is None and schema == b'https':
            ssl = _ssl.create_default_context()

        # Create the request.
        request = HttpRequest()
        request.method = method
        request.version = self._version
        request.body = body
        request.headers[b'Host'] = host
        request.on_url(url)

        # Apply headers.
        for key, val in self.headers.items():
            request.headers[key] = val
        for key, val in headers.items():
            request.headers[key] = val

        response = HttpResponse()
        response_error = False
        self._parser.set_target(response)

        await self.open((host, port), ssl=ssl)
        async with self._lock:
            self._writer.write(request.to_bytes())
            while True:
                data = await self._reader.read(buffer_length)
                if len(data) > 0:
                    self._parser.feed_data(data)
                    if response.is_complete():
                        break

        # Socket is unlocked at this point.
        if response.headers.get(b'Connection', b'') == b'close':
            await self.close()

        # If there are redirects and we're allowed to follow, then follow them.
        if allow_redirects and response.status_code in _HTTP_REDIRECTS:
            if max_redirects <= 0 or b'Location' not in response.headers:
                response_error = True
            else:
                response = await self.request(
                    (response.headers.get(b'Location') or response.headers.get(b'URI'))[0],
                    method, headers=headers, body=body, allow_redirects=True, max_redirects=max_redirects-1
                )

        # If we're errored or the response isn't complete, return a 500.
        if response_error or not response.is_complete():
            response.version = self._version
            response.body = b''
            response.status_code = 500
            response.status = b'Internal Server Error'
            return response
        else:
            return response
