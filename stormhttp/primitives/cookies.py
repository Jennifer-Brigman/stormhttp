import datetime
import typing
from .url import HttpUrl


# Global Variables
__all__ = [
    "HttpCookie",
    "HttpCookies"
]
_DEFAULT_COOKIE_META = (None, None, None, None, False, False)
_EPOCH = datetime.datetime.fromtimestamp(0)


class HttpCookie:
    def __init__(self, name: bytes, value: bytes, domain: typing.Optional[bytes]=None,
                 path: typing.Optional[bytes]=None, expires: typing.Optional[datetime.datetime]=None,
                 max_age: typing.Optional[int]=None, http_only: bool=False, secure: bool=False):
        self.name = name
        self.value = value
        self.domain = domain
        self.path = path
        self.expires = expires
        self._max_age = max_age
        self.http_only = http_only
        self.secure = secure
        self._max_age_set = datetime.datetime.utcnow()

    def __eq__(self, other) -> bool:
        return isinstance(other, HttpCookie) and self.name == other.cookie and self.value == other.value and \
               self.domain == other.domain and self.path == other.path and self.expires == other.expires and \
               self.http_only == other.http_only and self.secure == other.secure

    @property
    def max_age(self) -> typing.Optional[int]:
        return self._max_age

    @max_age.setter
    def max_age(self, max_age: typing.Optional[int]):
        self._max_age = max_age
        self._max_age_set = datetime.datetime.utcnow()

    def expire(self) -> None:
        """
        Expires the cookie and removes it's value.
        :return: None
        """
        self.expires = _EPOCH
        self.max_age = 0
        self.value = b''

    def expiration_datetime(self) -> typing.Optional[datetime.datetime]:
        """
        Returns the datetime object for when the HttpCookie will expire.
        If the HttpCookie is already expired, then it returns when it expired.
        If a None value is returned, it indicates that there is not current
        schedule for the HttpCookie to expire.
        :return: Datetime object or None.
        """
        expire_times = []
        if self._max_age is not None:
            expire_times.append(self._max_age_set + datetime.timedelta(seconds=self._max_age))
        if self.expires is not None:
            expire_times.append(self.expires)
        if len(expire_times) == 0:
            return None
        else:
            return min(expire_times)

    def is_expired(self) -> bool:
        expire_time = self.expiration_datetime()
        return expire_time is not None and datetime.datetime.utcnow() > expire_time

    def is_allowed_for_url(self, url: HttpUrl) -> bool:

        # First check to see if the cookie is for HTTPS only.
        if self.secure and url.schema != b'https':
            return False

        # Check that this is either a domain or sub-domain.
        if self.domain is not None:
            url_domains = url.host.split(b'.')
            cookie_domains = self.domain.split(b'.')
            if cookie_domains[0] == b'':  # This is to remove the '.google.com' "fix" for old browsers.
                cookie_domains = cookie_domains[1:]
            if len(cookie_domains) > len(url_domains):
                return False
            for i in range(-1, -len(cookie_domains)-1, -1):
                if url_domains[i] != cookie_domains[i]:
                    return False

        # Check this this is either a valid sub-path.
        if self.path is not None and not url.path.startswith(self.path):
            return False

        return True


class HttpCookies(dict):
    def __init__(self, *args, **kwargs):
        self._meta = {}
        self._changed = {}

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
                    cookie_crumbs.append(b'Expires=%b;' % expires.strftime("%a, %d %b %Y %H:%M:%S GMT").encode("ascii"))
                if max_age is not None:
                    cookie_crumbs.append(b'MaxAge=%d;' % max_age)
                cookies.append(b' '.join(cookie_crumbs))
            return b'\r\n'.join(cookies)
        else:
            return b'COOKIE: ' + b'; '.join(b'%b=%b' % (key, val) for key, val in self.items()) + b';'
