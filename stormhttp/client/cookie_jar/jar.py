import typing
from .abc import AbstractCookieJar, AbstractCookieJarStorage
from .storage import TemporaryCookieJarStorage
from ...primitives import HttpUrl, HttpCookies, HttpCookie

__all__ = [
    "CookieJar"
]


class CookieJar(AbstractCookieJar):
    def __init__(self, storage: typing.Optional[AbstractCookieJarStorage]=None):
        if storage is None:
            storage = TemporaryCookieJarStorage()
        AbstractCookieJar.__init__(self, storage)
        # Dictionary key tuple should be Name, Domain, Path
        self.cookies = {}  # type: typing.Dict[typing.Tuple[bytes, bytes], HttpCookie]

    def __len__(self) -> int:
        return len(self.cookies)

    def __contains__(self, cookie: HttpCookie) -> bool:
        cookie_key = (cookie.domain, cookie.path)
        return cookie_key in self.cookies

    def __iter__(self):
        return iter(self.cookies)

    def load_all_cookies(self):
        self.cookies = {}
        for cookie in self.storage.load_all_cookies():
            self.cookies[(cookie.domain, cookie.path)] = cookie

    def save_all_cookies(self):
        self.storage.save_all_cookies(list(self.cookies.values()))

    def get_cookies_for_url(self, url: HttpUrl) -> HttpCookies:
        cookies = HttpCookies()
        for cookie in self.cookies.values():
            if cookie.is_allowed_for_url(url):
                cookies.add(cookie)
        return cookies

    def update_cookies(self, url: HttpUrl, cookies: HttpCookies):
        for cookie in cookies:
            if cookie.is_allowed_for_url(url):
                cookie_key = (cookie.domain, cookie.path)
                self.cookies[cookie_key] = cookie
