import abc
import typing
from ...primitives import HttpCookie, HttpCookies, HttpUrl

__all__ = [
    "AbstractCookieJarStorage",
    "AbstractCookieJar"
]


class AbstractCookieJarStorage(abc.ABC):
    @abc.abstractmethod
    def load_all_cookies(self) -> typing.List[HttpCookie]:
        pass

    @abc.abstractmethod
    def save_all_cookies(self, cookies: typing.List[HttpCookie]) -> None:
        pass


class AbstractCookieJar(abc.ABC):
    def __init__(self, storage: typing.Optional[AbstractCookieJarStorage]):
        self.storage = storage

    @abc.abstractmethod
    def load_all_cookies(self) -> None:
        pass

    @abc.abstractmethod
    def save_all_cookies(self) -> None:
        pass

    @abc.abstractmethod
    def get_cookies_for_url(self, url: HttpUrl) -> HttpCookies:
        pass

    @abc.abstractmethod
    def update_cookies(self, url: HttpUrl, cookies: HttpCookies):
        pass
