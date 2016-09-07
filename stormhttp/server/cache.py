import asyncio
import datetime
import types
import typing
import warnings
from ..primitives import HttpRequest, HttpResponse
from ..primitives.cookies import _COOKIE_EXPIRE_FORMAT

__all__ = [
    "cache_control",
    "CACHE_CONTROL_PUBLIC",
    "CACHE_CONTROL_PRIVATE",
    "CACHE_CONTROL_NO_CACHE"
]
CACHE_CONTROL_PUBLIC = b'public'
CACHE_CONTROL_PRIVATE = b'private'
CACHE_CONTROL_NO_CACHE = b'no-cache, no-store'

_CACHE_METHODS = {b'GET', b'HEAD'}
_RESPONSE_304_NOT_MODIFIED = HttpResponse(status=b'Not Modified', status_code=304)
_MAX_AGE_MAXIMUM_VALUE = 31536000


def cache_control(cache_setting: bytes=CACHE_CONTROL_PRIVATE, max_age: int=None,
                  etag: typing.Callable[[HttpRequest], bytes]=None,
                  last_modified: typing.Callable[[HttpRequest], datetime.datetime]=None) -> typing.Callable[[HttpRequest], HttpResponse]:

    # Warning about the bound on Cache-Control: max-age greater than a year (RFC 2616 Section 14.9).
    if max_age is not None and max_age > _MAX_AGE_MAXIMUM_VALUE:
        warnings.warn(("Cache-Control: max-age should not be longer than 1 year (31536000 seconds) as this may be ignored by RFC compliant browsers. "
                      "See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.9 for more info."), UserWarning, stacklevel=2)
        max_age = _MAX_AGE_MAXIMUM_VALUE

    def wrapped(func: typing.Callable[[HttpRequest], typing.Union[HttpResponse, types.CoroutineType]]):

        cache_etag = None
        cache_last_modified = None
        cache_control_header = cache_setting
        if max_age is not None:
            cache_control_header += b', max-age=%d' % max_age
        not_modified_response = HttpResponse(status=b'Not Modified', status_code=304)
        not_modified_response.headers[b'Cache-Control'] = cache_control_header

        async def _async_cache(request: HttpRequest) -> HttpResponse:
            nonlocal cache_etag
            nonlocal cache_last_modified
            cache_active = False

            # Conditional request handling
            if request.method in _CACHE_METHODS:
                cache_active = True

                # Etag / If-None-Match
                if etag is not None and b'If-None-Match' in request.headers:
                    cache_etag = etag(request)
                    if cache_etag in request.headers[b'If-None-Match']:
                        not_modified_response.headers[b'Etag'] = cache_etag
                        return not_modified_response

                # Last-Modifed / If-Modified-Since
                if last_modified is not None and b'If-Modified-Since' in request.headers:
                    cache_last_modified = last_modified(request)
                    if datetime.datetime.strptime(request.headers[b'If-Modified-Since'][0].decode("utf-8"), _COOKIE_EXPIRE_FORMAT) >= cache_last_modified:
                        not_modified_response.headers[b'Last-Modified'] = cache_last_modified.strftime(_COOKIE_EXPIRE_FORMAT).encode("utf-8")
                        return not_modified_response

            response = await func(request)

            # Adding the headers to the HttpResponse on it's way out.
            if cache_active:
                response.headers[b'Cache-Control'] = cache_control_header
                if etag is not None:
                    if cache_etag is None:
                        cache_etag = etag(request)
                    response.headers[b'Etag'] = cache_etag
                if last_modified is not None:
                    if cache_last_modified is None:
                        cache_last_modified = last_modified(request)
                    response.headers[b'Last-Modified'] = cache_last_modified.strftime(_COOKIE_EXPIRE_FORMAT).encode("utf-8")

            return response

        async def _sync_cache(request: HttpRequest) -> HttpResponse:
            nonlocal cache_etag
            nonlocal cache_last_modified
            cache_active = False

            # Conditional request handling
            if request.method in _CACHE_METHODS:
                cache_active = True

                # Etag / If-None-Match
                if etag is not None and b'If-None-Match' in request.headers:
                    cache_etag = etag(request)
                    if cache_etag in request.headers[b'If-None-Match']:
                        not_modified_response.headers[b'Etag'] = cache_etag
                        return not_modified_response

                # Last-Modifed / If-Modified-Since
                if last_modified is not None and b'If-Modified-Since' in request.headers:
                    cache_last_modified = last_modified(request)
                    if datetime.datetime.strptime(request.headers[b'If-Modified-Since'][0].decode("utf-8"), _COOKIE_EXPIRE_FORMAT) >= cache_last_modified:
                        not_modified_response.headers[b'Last-Modified'] = cache_last_modified.strftime(_COOKIE_EXPIRE_FORMAT).encode("utf-8")
                        return not_modified_response

            response = func(request)

            # Adding the headers to the HttpResponse on it's way out.
            if cache_active:
                response.headers[b'Cache-Control'] = cache_control_header
                if etag is not None:
                    if cache_etag is None:
                        cache_etag = etag(request)
                    response.headers[b'Etag'] = cache_etag
                if last_modified is not None:
                    if cache_last_modified is None:
                        cache_last_modified = last_modified(request)
                    response.headers[b'Last-Modified'] = cache_last_modified.strftime(_COOKIE_EXPIRE_FORMAT).encode("utf-8")

            return response

        if asyncio.iscoroutinefunction(func):
            return _async_cache
        else:
            return _sync_cache
    return wrapped
