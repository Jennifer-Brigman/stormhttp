import collections
import datetime
import typing
import stormhttp


__all__ = [
    "setup"
]
_APP_KEY = "stormhttp_sessions_env"
_COOKIE_NAME = b"_stormhttp_session"


class AbstractStorage:
    def __init__(self, cookie_name: bytes=_COOKIE_NAME, domain: typing.Optional[bytes]=None,
                 max_age: typing.Optional[int]=None, path: typing.Optional[bytes]=b'/',
                 secure: bool=True, http_only: bool=False):
        self._cookie_name = cookie_name
        self._domain = domain
        self._max_age = max_age
        self._path = path
        self._secure = secure
        self._http_only = http_only

    async def load_session(self):
        raise NotImplementedError("AbstractStorage.load_session() is not implemented.")

    async def save_session(self, request: stormhttp.web.HTTPRequest, response: stormhttp.web.HTTPResponse, session:):
        raise NotImplementedError("AbstractStorage.save_session() is not implemented.")

    def load_cookie(self, request: stormhttp.web.HTTPRequest) -> None:
        cookie = request.cookies.get(self._cookie_name, None)
        return cookie

    def save_cookie(self, response: stormhttp.web.HTTPResponse, cookie: typing.Optional[bytes]) -> None:
        if cookie is None:
            response.cookies.expire_cookie(self._cookie_name)
        else:
            response.cookies[self._cookie_name] = cookie
            response.cookies.set_meta(
                self._cookie_name, domain=self._domain, path=self._path,
                max_age=self._max_age, http_only=self._http_only
            )


class Session(collections.MutableMapping):
    def __init__(self, identity, data: typing.Mapping[bytes, bytes]):
        self._mapping = {}
        self._identity = identity
        self._created = data.get("created", None)
        self._changed = False
        if self._created is None:
            self._created = datetime.datetime.now()
        else:
            self._created = datetime.datetime.fromtimestamp(self._created)
        self._mapping.update(data.get("session", {}))

    def expire_session(self):
        self._changed = True
        self._mapping = {}

    def __len__(self):
        return len(self._mapping)

    def __iter__(self):
        return iter(self._mapping)

    def __contains__(self, key):
        return key in self._mapping

    def __getitem__(self, key):
        return self._mapping[key]

    def __setitem__(self, key, value):
        self._mapping[key] = value
        self._changed = True

    def __delitem__(self, key):
        del self._mapping[key]
        self._changed = True


def setup(app: stormhttp.web.Application, storage_type: type(AbstractStorage)) -> None:
    """
    Registers the sessions middleware with the Application.
    :param app: Application to register the session with.
    :return: None
    """
    app.add_middleware(SessionMiddleware(storage_type))


class SessionMiddleware(stormhttp.web.AbstractMiddleware):
    def __init__(self, storage_type: type(AbstractStorage), *args, **kwargs):
        stormhttp.web.AbstractMiddleware.__init__(self)
        self._storage_type = storage_type
        self._args = args
        self._kwargs = kwargs

    async def on_request(self, request: stormhttp.web.HTTPRequest) -> None:
        if _COOKIE_NAME in request.cookies:
