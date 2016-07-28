import base64
import cryptography.fernet
import ultrajson as json
import typing
import stormhttp


__all__ = [
    "setup",
    "Session",
    "AbstractStorage",
    "SimpleStorage",
    "EncryptedFernetStorage"
]
_COOKIE_NAME = '_stormhttp_session'


class Session(dict):
    def __init__(self, identity, data: dict):
        dict.__init__({})
        self._identity = identity
        self._changed = False
        self._mapping = data

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


class AbstractStorage:
    def __init__(self, cookie_name: str=_COOKIE_NAME, domain: typing.Optional[str]=None,
                 max_age: typing.Optional[str]=None, path: typing.Optional[str]='/',
                 secure: bool=True, http_only: bool=True):
        self._cookie_name = cookie_name
        self._domain = domain
        self._max_age = max_age
        self._path = path
        self._secure = secure
        self._http_only = http_only

    async def load_session(self, request: stormhttp.web.HTTPRequest) -> Session:
        raise NotImplementedError("AbstractStorage.load_session() is not implemented.")

    async def save_session(self, request: stormhttp.web.HTTPRequest, response: stormhttp.web.HTTPResponse, session: Session):
        raise NotImplementedError("AbstractStorage.save_session() is not implemented.")

    def load_cookie(self, request: stormhttp.web.HTTPRequest) -> typing.Optional[bytes]:
        cookie = request.cookies.get(self._cookie_name, None)
        return cookie

    def save_cookie(self, response: stormhttp.web.HTTPResponse, cookie: typing.Optional[str]) -> None:
        if cookie is None:
            response.cookies.expire_cookie(self._cookie_name)
        else:
            response.cookies[self._cookie_name] = cookie
            response.cookies.set_meta(
                self._cookie_name, domain=self._domain, path=self._path,
                max_age=self._max_age, http_only=self._http_only
            )


class SimpleStorage(AbstractStorage):
    def __init__(self, cookie_name: str=_COOKIE_NAME,
                 domain: typing.Optional[str]=None, max_age: typing.Optional[int]=None,
                 path: typing.Optional[str]='/', secure: bool=True, http_only: bool=True):
        AbstractStorage.__init__(self, cookie_name, domain, max_age, path, secure, http_only)

    async def load_session(self, request: stormhttp.web.HTTPRequest) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, data={})
        else:
            try:
                return Session(None, data=json.loads(cookie.decode("utf-8")))
            except (ValueError, UnicodeDecodeError):
                return Session(None, data={})

    async def save_session(self, request: stormhttp.web.HTTPRequest, response: stormhttp.web.HTTPResponse, session: Session):
        self.save_cookie(response, json.dumps(session))


class EncryptedFernetStorage(AbstractStorage):
    def __init__(self, secret_key: typing.Union[str, bytes], cookie_name: str=_COOKIE_NAME,
                 domain: typing.Optional[str]=None, max_age: typing.Optional[int]=None,
                 path: typing.Optional[str]='/', secure: bool=True, http_only: bool=True):
        AbstractStorage.__init__(self, cookie_name, domain, max_age, path, secure, http_only)
        if isinstance(secret_key, bytes):
            secret_key = base64.urlsafe_b64encode(secret_key)
        self._fernet = cryptography.fernet.Fernet(secret_key)

    async def load_session(self, request: stormhttp.web.HTTPRequest) -> Session:
        cookie = self.load_cookie(request)
        if cookie is None:
            return Session(None, {})
        else:
            try:
                data = json.loads(self._fernet.decrypt(cookie).decode("utf-8"), encoding="utf-8")
                return Session(None, data)
            except cryptography.fernet.InvalidToken:
                return Session(None, {})

    async def save_session(self, request: stormhttp.web.HTTPRequest, response: stormhttp.web.HTTPResponse, session: Session):
        if len(session) == 0:
            self.save_cookie(response, '')
        else:
            self.save_cookie(response, self._fernet.encrypt(json.dumps(session).decode("utf-8")).encode("utf-8"))


def setup(app: stormhttp.web.Application, storage: AbstractStorage) -> None:
    """
    Registers the sessions middleware with the Application.
    :param app: Application to register the session with.
    :param storage: Storage to use for
    :return: None
    """
    app.add_middleware(SessionMiddleware(storage))


class SessionMiddleware(stormhttp.web.AbstractMiddleware):
    def __init__(self, storage: AbstractStorage, *args, **kwargs):
        stormhttp.web.AbstractMiddleware.__init__(self)
        self._storage = storage
        self._args = args
        self._kwargs = kwargs

    async def on_request(self, request: stormhttp.web.HTTPRequest) -> None:
        request.session = await self._storage.load_session(request)

    async def on_response(self, request: stormhttp.web.HTTPRequest, response: stormhttp.web.HTTPResponse):
        await self._storage.save_session(request, response, request.session)
