import typing
from .abc import AbstractCookieJarStorage
from ...primitives import HttpCookie

__all__ = [
    "TemporaryCookieJarStorage"
]


class TemporaryCookieJarStorage(AbstractCookieJarStorage):
    def __init__(self):
        AbstractCookieJarStorage.__init__(self)

    def load_all_cookies(self) -> typing.List[HttpCookie]:
        pass

    def save_all_cookies(self, cookies: typing.List[HttpCookie]):
        pass
