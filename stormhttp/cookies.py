import datetime
import typing


# Global Variables
__all__ = [
    "HttpCookies"
]
_DEFAULT_COOKIE_META = (None, None, None, None, False, False)


class HttpCookies(dict):
    def __init__(self, *args, **kwargs):
        self._meta = {}
        self._changed = {}
        self.update(*args, **kwargs)

    def __getitem__(self, key: bytes) -> bytes:
        dict.__getitem__(self, key)

    def __setitem__(self, key: bytes, val: bytes) -> None:
        dict.__setitem__(self, key, val)
        self._changed[key] = True

    def __contains__(self, key: bytes) -> bool:
        return dict.__contains__(self, key)

    def __repr__(self):
        return dict.__repr__(self)

    def update(self, *args, **kwargs):
        for key, val in dict(*args, **kwargs).items():
            self[key] = val
            self._changed[key] = False

    def is_changed(self) -> bool:
        return any(self._changed.values())

    def set_meta(self, cookie: bytes, domain: typing.Optional[bytes]=None, path: typing.Optional[bytes]=None,
                 expires: typing.Optional[datetime.datetime]=None, max_age: typing.Optional[int]=None,
                 http_only: bool=False, secure: bool=False):
        if cookie not in self:
            raise KeyError(str(cookie))
        if max_age is not None:

            # This case is used to make max_age work with IE. IE does not support MaxAge in cookies.
            max_age_dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
            if expires is not None:
                expires = min(expires, max_age_dt)
            else:
                expires = max_age_dt
        self._meta[cookie] = (domain, path, expires, max_age, http_only, secure)
        self._changed[cookie] = True

    def get_meta(self, cookie: bytes) -> typing.Tuple[typing.Optional[bytes], typing.Optional[bytes],
                                                      typing.Optional[datetime.datetime], bool, bool]:
        if cookie not in self:
            raise KeyError(str(cookie))
        return self._meta.get(cookie, _DEFAULT_COOKIE_META)

    def expire(self, cookie: bytes):
        if cookie not in self:
            raise KeyError(str(cookie))
        self._meta[cookie] = _DEFAULT_COOKIE_META
        self._changed[cookie] = True
        self[cookie] = b''

    def to_bytes(self, set_cookie: bool=False) -> bytes:
        if set_cookie:
            cookies = []
            for cookie, changed in self._changed.items():
                if not changed:
                    continue
                cookie_crumbs = [b'SET-COOKIE:', b'%b=%b;' % (cookie, self.get(cookie))]
                domain, path, expires, max_age, http_only, secure = self._meta.get(cookie, _DEFAULT_COOKIE_META)
                if http_only:
                    cookie_crumbs.append(b'HttpOnly;')
                if secure:
                    cookie_crumbs.append(b'Secure;')
                if domain is not None:
                    cookie_crumbs.append(b'Domain=%b;' % domain)
                if path is not None:
                    cookie_crumbs.append(b'Path=%b;' % path)
                if expires is not None:
                    cookie_crumbs.append(b'Expires=%b;' %
                                         expires.strftime("%a, %d %b %Y %H:%M:%S GMT").encode("ascii"))
                if max_age is not None:
                    cookie_crumbs.append(b'MaxAge=%d;' % max_age)
                cookies.append(b' '.join(cookie_crumbs))
            return b'\r\n'.join(cookies)
        else:
            return b'COOKIE: ' + b'; '.join(b'%b=%b' % (key, val) for key, val in self.items()) + b';'
