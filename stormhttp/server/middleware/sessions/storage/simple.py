from .abc import AbstractServerSessionStorage, _COOKIE_KEY

__all__ = [
    "SimpleServerSessionStorage"
]


class SimpleServerSessionStorage(AbstractServerSessionStorage):
    def __init__(self, cookie_key: bytes=_COOKIE_KEY):
        AbstractServerSessionStorage.__init__(self, cookie_key)


