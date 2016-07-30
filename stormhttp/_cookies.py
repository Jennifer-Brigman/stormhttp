import collections
import datetime
import re
import typing
from ._constants import HTTP_DATETIME_FORMAT

# Global Variables
_COOKIE_REGEX = re.compile(r'([^\s=;]+)(?:=([^=;]+))?(?:;|$)')
_COOKIE_EXPIRE_TIME = datetime.datetime.utcfromtimestamp(0)


class HTTPCookies(collections.MutableMapping):
    def __init__(self, raw_cookies: bytes):
        self._cookies = {}
        self._changed = set()
        self._meta = {}
        for key, value in _COOKIE_REGEX.findall(raw_cookies.decode("utf-8")):
            self._cookies[key] = value

    def get(self, key: str, default=None) -> str:
        return self._cookies.get(key, default)

    def __getitem__(self, item: str) -> str:
        return self._cookies[item]

    def __setitem__(self, key: str, value: str) -> None:
        self._cookies[key] = value
        self._changed.add(key)

    def __contains__(self, item: str) -> bool:
        return item in self._cookies

    def __len__(self) -> int:
        return len(self._cookies)

    def __delitem__(self, item: str):
        self[item] = ""

    def __iter__(self):
        return iter(self._cookies)

    def set_meta(self, cookie: str,
                 domain: typing.Optional[str]=None,
                 path: typing.Optional[str]=None,
                 expires: typing.Optional[datetime.datetime]=None,
                 max_age: typing.Optional[int]=None, http_only: bool=False,
                 secure: bool=False) -> None:
        """
        Sets the meta information for the cookie including the HttpOnly and
        Secure flags. MaxAge is not supported by IE and is converted into
        an Expires flag instead. Overwrites previous meta values.
        :param cookie: Cookie to modify.
        :param domain: Domain where the cookie is valid.
        :param path: Path and sub-paths where the cookie is valid.
        :param expires: Datetime when the cookie is to expire.
        :param max_age: Maximum age in seconds for the cookie to live.
        :param http_only: If True, disallows Javascript from accessing the cookie.
                          Prevents XSS attacks from hijacking session tokens.
        :param secure:    If True, disallows sending the cookie over non-secure HTTP.
        :return: None
        """
        if cookie not in self._cookies:
            raise KeyError(str(cookie))
        if max_age is not None:
            max_age_expire = datetime.datetime.utcnow() + datetime.timedelta(max_age)
            if expires is not None:
                expires = min(expires, max_age_expire)
            else:
                expires = max_age_expire
        self._changed.add(cookie)
        self._meta[cookie] = (domain, path, expires, http_only, secure)

    def expire_cookie(self, cookie: str) -> None:
        """
        Forces a cookie to expire by setting all it's values to empty
        strings and applies an expired timestamp to it.
        :param cookie: Cookie to expire.
        :return: None
        """
        if cookie not in self._cookies:
            raise KeyError(str(cookie))
        self._cookies[cookie] = ""
        self.set_meta(cookie, expires=_COOKIE_EXPIRE_TIME)

    def to_header(self, set_cookie: bool=False) -> bytes:
        """
        Converts the cookies to bytes to be sent.
        :param set_cookie: If True, will only convert changed
                           cookies to bytes and use the Set-Cookie header.
        :return: Bytes representing the cookies for HTTP.
        """
        if set_cookie:
            _no_meta = (None, None, None, False, False)
            cookie_headers = []
            for cookie in self._cookies:
                if cookie in self._changed:
                    domain, path, expires, http_only, secure = self._meta.get(cookie, _no_meta)
                    if expires is not None:
                        expires = expires.strftime(HTTP_DATETIME_FORMAT)
                    cookie_headers.append("Set-Cookie: %s=%s;%s%s%s%s%s" % (
                        cookie, self._cookies[cookie],
                        " Domain=%s;" % domain if domain is not None else "",
                        " Path=%s;" % path if path is not None else "",
                        " Expires=%s;" % expires if expires is not None else "",
                        " HttpOnly;" if http_only else "",
                        " Secure;" if secure else ""
                    ))
            return "\r\n".join(cookie_headers)
        else:
            return "Cookie: %s" % (" ".join("%s=%s;" % (key, value) for key, value in self._cookies.items()))
