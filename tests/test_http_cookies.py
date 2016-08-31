import unittest


def _make_http_url(url: bytes):
    from stormhttp.primitives import HttpUrl
    import httptools
    parsed_url = httptools.parse_url(url)
    print(parsed_url.host)
    return HttpUrl(url, parsed_url.schema, parsed_url.host, parsed_url.port,
                   parsed_url.path, parsed_url.query, parsed_url.fragment, parsed_url.userinfo)


class TestHttpCookies(unittest.TestCase):
    def test_cookies_expired(self):
        import datetime
        from stormhttp.primitives import HttpCookie
        cookie = HttpCookie(b'foo', b'bar')

        cookie.expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        self.assertFalse(cookie.is_expired())

        cookie.expires = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
        self.assertTrue(cookie.is_expired())

    def test_cookies_allowed_for_url(self):
        from stormhttp.primitives import HttpCookie
        cookie = HttpCookie(b'foo', b'bar', domain=b'.google.com', secure=True)
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com')))
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://maps.google.com')))

        # Path shouldn't matter here.
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com/test')))

        # Neither should queries.
        self.assertTrue(cookie.is_allowed_for_url(_make_http_url(b'https://www.google.com?foo=bar')))

        # Secure cookie but sent over HTTP.
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'http://www.google.com')))

        # Completely incorrect domain name
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'https://www.github.com')))

        # Almost incorrect domain name
        self.assertFalse(cookie.is_allowed_for_url(_make_http_url(b'https://www.ggoogle.com')))
