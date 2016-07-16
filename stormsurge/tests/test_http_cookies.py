import unittest


class TestHTTPCookies(unittest.TestCase):
    def test_create_cookie(self):
        from stormsurge._cookies import HTTPCookies
        cookie = HTTPCookies(b'')
        self.assertEqual(cookie.to_bytes(), b'Cookie: ')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'')

        cookie = HTTPCookies(b'a=1;')
        self.assertEqual(cookie.to_bytes(), b'Cookie: a=1;')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'')

        cookie[b'a'] = b'2'
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=2;')

    def test_meta_cookie(self):
        import datetime
        from stormsurge._cookies import HTTPCookies
        cookie = HTTPCookies(b'a=1;')
        cookie.set_meta(b'a', http_only=True)
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; HttpOnly;')

        cookie.set_meta(b'a', secure=True)
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Secure;')

        cookie.set_meta(b'a', expires=datetime.datetime.utcfromtimestamp(1))
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Expires=Thu, 01 Jan 1970 00:00:01 UTC;')

        cookie.set_meta(b'a', path=b'/test')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Path=/test;')

        cookie.set_meta(b'a', domain=b'.example.com')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Domain=.example.com;')

    def test_expire_cookie(self):
        import datetime
        from stormsurge._cookies import HTTPCookies, _COOKIE_EXPIRE_FORMAT
        cookie = HTTPCookies(b'a=1;')
        cookie.expire_cookie(b'a')
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=; Expires=Thu, 01 Jan 1970 00:00:00 UTC;')

        cookie = HTTPCookies(b'a=1;')
        cookie.set_meta(b'a', max_age=0)
        now = datetime.datetime.utcnow().strftime(_COOKIE_EXPIRE_FORMAT).encode("latin-1")
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Expires=%b;' % now)

        cookie = HTTPCookies(b'a=1;')
        now = datetime.datetime.utcnow()
        cookie.set_meta(b'a', expires=now)
        now = now.strftime(_COOKIE_EXPIRE_FORMAT).encode("latin-1")
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Expires=%b;' % now)

        cookie = HTTPCookies(b'a=1;')
        now = datetime.datetime.utcnow()
        cookie.set_meta(b'a', expires=now, max_age=10)
        now = now.strftime(_COOKIE_EXPIRE_FORMAT).encode("latin-1")
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Expires=%b;' % now)

        cookie = HTTPCookies(b'a=1;')
        now = datetime.datetime.now()
        later = now + datetime.timedelta(seconds=10)
        cookie.set_meta(b'a', expires=now, max_age=0)
        now = now.strftime(_COOKIE_EXPIRE_FORMAT).encode("latin-1")
        self.assertEqual(cookie.to_bytes(set_cookie=True), b'Set-Cookie: a=1; Expires=%b;' % now)

    def test_cookie_multiple(self):
        from stormsurge._cookies import HTTPCookies
        cookie = HTTPCookies(b'a=1; b=2;')
        self.assertIn(cookie.to_bytes(), [
            b'Cookie: a=1; b=2;',
            b'Cookie: b=2; a=1;'
        ])

        cookie[b'a'] = b'3'
        cookie[b'b'] = b'4'
        self.assertIn(cookie.to_bytes(set_cookie=True), [
            b'Set-Cookie: a=3;\r\nSet-Cookie: b=4;',
            b'Set-Cookie: b=4;\r\nSet-Cookie: a=3;'
        ])

        for key in cookie:
            self.assertIn(key, [b'a', b'b'])
            self.assertIn(cookie[key], [b'3', b'4'])

        self.assertTrue(b'a' in cookie)
        self.assertFalse(b'c' in cookie)
        del cookie[b'a']
        self.assertEqual(cookie[b'a'], b'')

        with self.assertRaises(KeyError):
            cookie.set_meta(b'c')
        with self.assertRaises(KeyError):
            cookie.expire_cookie(b'c')


