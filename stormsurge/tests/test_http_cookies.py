import unittest


class TestHTTPCookies(unittest.TestCase):
    def test_create_cookie(self):
        from stormsurge._cookies import HTTPCookies
        cookie = HTTPCookies(b'')
        self.assertEqual(cookie.to_bytes(), b'Cookie: \r\n')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'')

        cookie = HTTPCookies(b'a=1;')
        self.assertEqual(cookie.to_bytes(), b'Cookie: a=1;\r\n')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'')

        cookie[b'a'] = b'2'
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=2;\r\n')

    def test_meta_cookie(self):
        import datetime
        from stormsurge._cookies import HTTPCookies
        cookie = HTTPCookies(b'a=1;')
        cookie.set_meta(b'a', http_only=True)
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; HttpOnly;\r\n')

        cookie.set_meta(b'a', secure=True)
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Secure;\r\n')

        cookie.set_meta(b'a', expires=datetime.datetime.utcfromtimestamp(1))
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Expires=Thu, 01 Jan 1970 00:00:01 UTC;\r\n')

        cookie.set_meta(b'a', path=b'/test')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Path=/test;\r\n')

        cookie.set_meta(b'a', domain=b'.example.com')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Domain=.example.com;\r\n')

    def test_expire_cookie(self):
        from stormsurge._cookies import HTTPCookies
        cookie = HTTPCookies(b'a=1;')
        cookie.expire_cookie(b'a')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=; Expires=Thu, 01 Jan 1970 00:00:00 UTC;\r\n')