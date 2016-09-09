import abc
import datetime
import json
from ..session import ServerSession
from .....primitives import HttpCookie

__all__ = [
    "AbstractServerSessionStorage"
]
_COOKIE_KEY = b'stormhttp_session'


class AbstractServerSessionStorage(abc.ABC):
    def __init__(self, cookie_key: bytes=_COOKIE_KEY, domain: bytes=None, path: bytes=b'/',
                 expires: datetime.datetime=None, max_age: int=None, http_only: bool=True, secure: bool=False):
        self.cookie_key = cookie_key
        self.domain = domain
        self.path = path
        self.expires = expires
        self.max_age = max_age
        self.http_only = http_only
        self.secure = secure

    @abc.abstractmethod
    def load_session(self, cookie_session: bytes) -> ServerSession:
        pass

    @abc.abstractmethod
    def save_session(self, session: ServerSession) -> bytes:
        pass

    @abc.abstractmethod
    def new_session(self) -> ServerSession:
        pass


