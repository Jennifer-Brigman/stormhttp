import json
from .abc import AbstractServerSessionStorage, _COOKIE_KEY
from ..session import ServerSession

__all__ = [
    "SimpleServerSessionStorage"
]


class SimpleServerSessionStorage(AbstractServerSessionStorage):
    def __init__(self, cookie_key: bytes=_COOKIE_KEY):
        AbstractServerSessionStorage.__init__(self, cookie_key)

    def load_session(self, cookie_session: bytes):
        session_data = None
        try:
            session_data = json.loads(cookie_session.decode("utf-8"))
        except UnicodeDecodeError:
            pass
        except json.JSONDecodeError:
            pass
        if session_data is None:
            return self.new_session()
        else:
            return ServerSession(None, session_data)

    def save_session(self, session: ServerSession) -> bytes:
        return json.dumps(session).encode("utf-8")

    def new_session(self) -> ServerSession:
        return ServerSession(None, {})
