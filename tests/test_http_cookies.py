import unittest


def _make_http_url(url: bytes):
    from stormhttp import HttpUrl
    import httptools
    parsed_url = httptools.parse_url(url)
    print(parsed_url.host)
    return HttpUrl(url, parsed_url.schema, parsed_url.host, parsed_url.port,
                   parsed_url.path, parsed_url.query, parsed_url.fragment, parsed_url.userinfo)


class TestHttpCookies(unittest.TestCase):
    def test_cookies_expired(self):
        import datetime
        from stormhttp import HttpCookie
        cookie = HttpCookie(b'foo', b'bar')

        cookie.expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        self.assertFalse(cookie.is_expired())

        cookie.expires = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
        self.assertTrue(cookie.is_expired())

    def test_cookies_allowed_for_url_domain(self):
        from stormhttp import HttpCookie
        cookie = HttpCookie(domain=b'www.google.com', secure=True)
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com')))

        # Path shouldn't matter here.
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com/test')))

        # Neither should queries.
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com?foo=bar')))

        # Parents don't get sub-domain cookies.
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'https://google.com')))

        # Secure cookie but sent over HTTP.
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'http://www.google.com')))

        # Completely incorrect domain name
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'https://www.github.com')))

        # Almost incorrect domain name
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'https://www.ggoogle.com')))

    def test_cookies_allowed_for_url_path(self):
        from stormhttp import HttpCookie
        cookie = HttpCookie(path=b'/foo')

        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com/foo')))
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com/foobar')))
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com/bar')))

    def test_cookies_insecure(self):
        from stormhttp import HttpCookie
        cookie = HttpCookie(domain=b'www.google.com')

        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'http://www.google.com')))
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com')))

    def test_cookies_dot_prefix(self):
        from stormhttp import HttpCookie
        cookie = HttpCookie(domain=b'.google.com')

        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'http://www.google.com')))
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'http://google.com')))

    def test_cookies_expire_times(self):
        from stormhttp import HttpCookie
        import datetime
        import time
        cookie = HttpCookie()

        # This cookie is shown never to expire.
        self.assertFalse(cookie.is_expired())
        self.assertIsNone(cookie.expiration_datetime())

        # This cookie will expire eventually.
        now = datetime.datetime.utcnow()
        future = now + datetime.timedelta(seconds=1)
        cookie = HttpCookie(expires=future)
        self.assertFalse(cookie.is_expired())
        self.assertEqual(cookie.expiration_datetime(), future)

        # Sleep, allow the cookie to expire naturally.
        time.sleep(1)

        # Check that the cookie is expired.
        self.assertTrue(cookie.is_expired())

        # This cookie will expire in two seconds.
        cookie = HttpCookie(max_age=1)
        self.assertFalse(cookie.is_expired())

        # Sleep, allow the cookie to expire naturally.
        time.sleep(1)

        # Check that the cookie is expired.
        self.assertTrue(cookie.is_expired())
