import datetime
import typing
from .url import HttpUrl


# Global Variables
__all__ = [
    "HttpCookie",
    "HttpCookies"
]
_EPOCH = datetime.datetime.fromtimestamp(0)
_COOKIE_EXPIRE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
_COOKIE_DELIMITER = b' '
_COOKIE_SUBDOMAIN_DELIMITER = b'.'
_COOKIE_FORMAT_DOMAIN = b'Domain=%b;'
_COOKIE_FORMAT_PATH = b'Path=%b;'
_COOKIE_FORMAT_EXPIRES = b'Expires=%b;'
_COOKIE_FORMAT_MAX_AGE = b'MaxAge=%d;'
_COOKIE_FORMAT_HTTP_ONLY = b'HttpOnly;'
_COOKIE_FORMAT_SECURE = b'Secure;'
_COOKIE_FORAMT_KEY_VALUE = b'%b=%b;'
_HTTPS_SCHEMA = b'https'
_HTTP_HEADER_COOKIE = b'COOKIE: %b'
_HTTP_HEADER_SET_COOKIE = b'SET-COOKIE:'


class HttpCookie:
    def __init__(self, domain: typing.Optional[bytes]=None, path: typing.Optional[bytes]=None,
                 expires: typing.Optional[datetime.datetime]=None, max_age: typing.Optional[int]=None,
                 http_only: bool=False, secure: bool=False):
        self.values = {}  # type: typing.Dict[bytes, bytes]
        self.domain = domain
        self.path = path
        self.expires = expires
        self._max_age = max_age
        self.http_only = http_only
        self.secure = secure
        self._max_age_set = datetime.datetime.utcnow()

    def __eq__(self, other) -> bool:
        return isinstance(other, HttpCookie) and self.domain == other.domain and self.path == other.path

    @property
    def max_age(self) -> typing.Optional[int]:
        return self._max_age

    @max_age.setter
    def max_age(self, max_age: typing.Optional[int]):
        self._max_age = max_age
        self._max_age_set = datetime.datetime.utcnow()

    def expire(self) -> None:
        """
        Expires the cookie and removes all the values.
        :return: None
        """
        self.expires = _EPOCH
        self.max_age = 0
        for key in self.values.keys():
            self.values[key] = b''

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
        if not expire_times:
            return None
        else:
            return min(expire_times)

    def is_expired(self) -> bool:
        expire_time = self.expiration_datetime()
        return expire_time is not None and datetime.datetime.utcnow() > expire_time

    def is_allowed_for_url(self, url: HttpUrl) -> bool:

        # First check to see if the cookie is for HTTPS only.
        if self.secure and url.schema != _HTTPS_SCHEMA:
            return False

        # Check that this is either a domain or sub-domain.
        if self.domain is not None:
            url_domains = url.host.split(_COOKIE_SUBDOMAIN_DELIMITER)
            cookie_domains = self.domain.split(_COOKIE_SUBDOMAIN_DELIMITER)
            if cookie_domains[0] == b'':  # This is to remove the '.google.com' "fix" for old browsers.
                cookie_domains = cookie_domains[1:]
            len_cookie_domains = len(cookie_domains)
            if len_cookie_domains > len(url_domains):
                return False
            for i in range(-1, -len_cookie_domains-1, -1):
                if url_domains[i] != cookie_domains[i]:
                    return False

        # Check this this is either a valid sub-path.
        if self.path is not None and not url.path.startswith(self.path):
            return False

        return True

    def __repr__(self):
        return "<HttpCookie values={} domain={} path={}>".format(self.values, self.domain, self.path)


class HttpCookies(dict):
    def __setitem__(self, key: typing.Tuple[bytes, bytes], value: HttpCookie) -> None:
        dict.__setitem__(self, key, value)

    def __getitem__(self, key: typing.Tuple[bytes, bytes]) -> HttpCookie:
        return dict.__getitem__(self, key)

    def add(self, cookie: HttpCookie):
        self[(cookie.domain, cookie.path)] = cookie

    def remove(self, cookie: HttpCookie):
        cookie_key = (cookie.domain, cookie.path)
        if cookie_key in self:
            dict.__delitem__(self, cookie_key)

    def all(self) -> typing.Dict[bytes, bytes]:
        values = {}
        for cookie in self.values():
            for key, value in cookie.values.items():
                values[key] = value
        return values

    def to_bytes(self, set_cookie: bool=False) -> bytes:
        if set_cookie:
            all_cookie_crumbs = []
            for cookie in self.values():
                cookie_crumbs = [_HTTP_HEADER_SET_COOKIE]
                for key, value in cookie.values.items():
                    cookie_crumbs.append(_COOKIE_FORAMT_KEY_VALUE % (key, value))

                if cookie.domain is not None:
                    cookie_crumbs.append(_COOKIE_FORMAT_DOMAIN % cookie.domain)
                if cookie.path is not None:
                    cookie_crumbs.append(_COOKIE_FORMAT_PATH % cookie.path)
                if cookie.expires is not None:
                    cookie_crumbs.append(_COOKIE_FORMAT_EXPIRES % cookie.expires.strftime(_COOKIE_EXPIRE_FORMAT).encode("utf-8"))
                if cookie.max_age is not None:
                    cookie_crumbs.append(_COOKIE_FORMAT_MAX_AGE % cookie.max_age)
                if cookie.http_only:
                    cookie_crumbs.append(_COOKIE_FORMAT_HTTP_ONLY)
                if cookie.secure:
                    cookie_crumbs.append(_COOKIE_FORMAT_SECURE)

                all_cookie_crumbs.append(_COOKIE_DELIMITER.join(cookie_crumbs))
            return b'\r\n'.join(all_cookie_crumbs)
        else:
            all_values = {}
            for cookie in self.values():
                for key, value in cookie.values.items():
                    if key not in all_values:
                        all_values[key] = value
            return _HTTP_HEADER_COOKIE % _COOKIE_DELIMITER.join([_COOKIE_FORAMT_KEY_VALUE % (key, all_values[key]) for key in all_values])
