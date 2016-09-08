import abc
import datetime
import json
from stormhttp.primitives import HttpRequest, HttpResponse, HttpCookie

__all__ = [
    "AbstractServerSessionStorage"
]
_COOKIE_KEY = b'stormhttp_session'


class AbstractServerSessionStorage(abc.ABC):
    def __init__(self, cookie_key: bytes=_COOKIE_KEY, domain: bytes=None, path: bytes=b'/',
                 expires: datetime.datetime=None, max_age: int=None, http_only: bool=True, secure: bool=False):
        self._cookie_key = cookie_key
        self._domain = domain
        self._path = path
        self._expires = expires
        self._max_age = max_age
        self._http_only = http_only
        self._secure = secure

    def load_cookie(self, request: HttpRequest) -> HttpCookie:
        cookie_key = (self._domain, self._path)
        cookie = request.cookies.get(cookie_key)
        return cookie if cookie is None else HttpCookie()

    def save_cookie(self, response: HttpResponse, session) -> None:
        cookie_key = (self._domain, self._path)
        cookie = response.cookies.get(cookie_key)
        if cookie is None:
            cookie = HttpCookie()
        if cookie:
            cookie.values[self._cookie_key] = json.dumps(session).encode("utf-8")



