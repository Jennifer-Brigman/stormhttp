import typing
from .primitives import HttpResponse

__all__ = [
    "HttpError",
    "Http101SwitchingProtocols",
    "Http301MovedPermanently",
    "Http304NotModified",
    "Http400BadRequest",
    "Http401Unauthorized",
    "Http403Forbidden",
    "Http404NotFound",
    "Http405MethodNotAllowed",
    "Http500InternalServerError",
    "Http501NotImplemented",
    "Http502BadGateway",
    "Http503ServiceUnavailable",
    "Http505HttpVersionNotSupported",
    "SslError",
    "SslCertificateError",
    "SslCertificateVerificationError",
    "SslCertificateInsecureError",
    "SslEofError"
]


class HttpError(Exception):
    def __init__(self, status: bytes, status_code: int, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        self.response = HttpResponse()
        if headers is not None:
            for key, val in headers:
                self.response.headers[key] = val
        self.response.body = body
        self.response.status = status
        self.response.status_code = status_code
        self.response.version = b'1.1'
        super(HttpError, self).__init__()

    def __str__(self) -> str:
        return str(self.response.to_bytes())

    def __repr__(self) -> str:
        return "<HttpError status={} status_code={}>".format(self.response.status, self.response.status_code)


class Http101SwitchingProtocols(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Switching Protocols', 101, body, headers)


class Http301MovedPermanently(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Moved Permanently', 301, body, headers)


class Http304NotModified(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Not Modified', 304, body, headers)


class Http400BadRequest(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Bad Request', 400, body, headers)


class Http401Unauthorized(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Unauthorized', 401, body, headers)


class Http403Forbidden(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Forbidden', 403, body, headers)


class Http404NotFound(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Not Found', 404, body, headers)


class Http405MethodNotAllowed(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Method Not Allowed', 405, body, headers)


class Http500InternalServerError(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Internal Server Error', 500, body, headers)


class Http501NotImplemented(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Not Implemented', 501, body, headers)


class Http502BadGateway(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Bad Gateway', 502, body, headers)


class Http503ServiceUnavailable(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'Service Unavailable', 503, body, headers)


class Http505HttpVersionNotSupported(HttpError):
    def __init__(self, body: bytes=b'', headers: typing.Iterable[typing.Tuple[bytes, bytes]]=None):
        HttpError.__init__(self, b'HTTP Version Not Supported', 505, body, headers)


class SslError(Exception):
    pass


class SslCertificateError(SslError):
    pass


class SslCertificateVerificationError(SslCertificateError):
    pass


class SslCertificateInsecureError(SslCertificateError):
    pass


class SslEofError(SslError):
    pass