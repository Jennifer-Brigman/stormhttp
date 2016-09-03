import typing
from .abc import AbstractCookieJar, AbstractCookieJarStorage
from .storage import TemporaryCookieJarStorage
from ...primitives import HttpUrl, HttpCookie, HttpCookies

__all__ = [
    "CookieJar"
]


class CookieJar(AbstractCookieJar):
    def __init__(self, storage: typing.Optional[AbstractCookieJarStorage]=None):
        if storage is None:
            storage = TemporaryCookieJarStorage()
        AbstractCookieJar.__init__(self, storage)
        # Dictionary key tuple should be Name, Domain, Path
        self._cookies = {}  # type: typing.Dict[typing.Tuple[bytes, bytes, bytes], HttpCookie]

    def __len__(self) -> int:
        return len(self._cookies)

    def __contains__(self, cookie: HttpCookie) -> bool:
        cookie_key = (cookie.name, cookie.domain, cookie.path)
        return cookie_key in self._cookies and self._cookies[cookie_key] == cookie

    def __iter__(self):
        return iter(self._cookies)

    def load_all_cookies(self):
        self._cookies = {}
        self.update_cookies(self.storage.load_all_cookies())

    def save_all_cookies(self):
        self.storage.save_all_cookies(list(self._cookies.values()))

    def get_cookies_for_url(self, url: HttpUrl) -> typing.List[HttpCookie]:
        cookies = []
        for cookie in self._cookies.values():
            if cookie.is_allowed_for_url(url):
                cookies.append(cookie)
        return cookies

    def update_cookies(self, cookies: typing.List[HttpCookie]):
        for cookie in cookies:
            cookie_key = (cookie.name, cookie.domain, cookie.path)
            self._cookies[cookie_key] = cookie


