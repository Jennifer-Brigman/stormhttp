import unittest


class TestCookies(unittest.TestCase):
    def test_create_cookie(self):
        import stormsurge.http
        cookie = stormsurge.http.HTTPCookie(b'a=1; b=2; c=3')

        # __getitem__
        self.assertEqual(cookie.get(b'a'), b'1')
        self.assertEqual(cookie.get(b'b'), b'2')
        self.assertEqual(cookie.get(b'c'), b'3')

        # __contains__
        self.assertTrue(b'a' in cookie)
        self.assertFalse(b'd' in cookie)

        # __setitem__
        self.assertFalse(cookie.is_changed())
        cookie[b'a'] = b'4'
        self.assertEqual(cookie[b'a'], b'4')
        self.assertTrue(cookie.is_changed())

        # __len__
        self.assertEqual(len(cookie), 3)

        # expires
        import datetime
        self.assertIsNone(cookie.get_expire_time())
        expire_time = datetime.datetime.now()
        cookie.set_expire_time(expire_time)
        self.assertIsNotNone(cookie.get_expire_time())
        self.assertEqual(cookie.get_expire_time(), expire_time)

        # secure
        self.assertFalse(cookie.is_secure())
        cookie.set_secure(True)
        self.assertTrue(cookie.is_secure())

        # httponly
        self.assertFalse(cookie.is_http_only())
        cookie.set_http_only(True)
        self.assertTrue(cookie.is_http_only())

    def test_export_cookie(self):
        import datetime
        import stormsurge.http
        timestamp = datetime.datetime.utcnow().strftime(stormsurge.http._COOKIE_EXPIRE_FORMAT).encode("latin-1")
        raw_cookie1 = b'a=1; Expires=%b; HttpOnly; Secure;' % timestamp
        cook_cookie1 = b'Cookie: ' + raw_cookie1
        cookie = stormsurge.http.HTTPCookie(raw_cookie1)
        self.assertEqual(cookie.to_bytes(), cook_cookie1)

    def test_import_cookie(self):
        import datetime
        import time
        import stormsurge.http

        # Natural expiring
        timestamp = (datetime.datetime.utcnow() + datetime.timedelta(seconds=1)).strftime(stormsurge.http._COOKIE_EXPIRE_FORMAT).encode("latin-1")
        raw_cookie = b'Expires=%b;' % timestamp
        cookie = stormsurge.http.HTTPCookie(raw_cookie)
        self.assertFalse(cookie.is_expired())
        time.sleep(2)
        self.assertTrue(cookie.is_expired())

        # Expire explicitly
        timestamp = (datetime.datetime.utcnow() + datetime.timedelta(seconds=1000)).strftime(stormsurge.http._COOKIE_EXPIRE_FORMAT).encode("latin-1")
        raw_cookie = b'Expires=%b;' % timestamp
        cookie = stormsurge.http.HTTPCookie(raw_cookie)
        self.assertFalse(cookie.is_expired())
        cookie.expire_cookie()
        self.assertTrue(cookie.is_expired())

        # Flags
        cookie = stormsurge.http.HTTPCookie(b'a=1; HttpOnly;')
        self.assertTrue(cookie.is_http_only())
        self.assertFalse(cookie.is_secure())
        self.assertIsNone(cookie.get_expire_time())

        cookie = stormsurge.http.HTTPCookie(b'a=1; Secure;')
        self.assertFalse(cookie.is_http_only())
        self.assertTrue(cookie.is_secure())
        self.assertIsNone(cookie.get_expire_time())

        cookie = stormsurge.http.HTTPCookie(b'a=1; HttpOnly; Secure;')
        self.assertTrue(cookie.is_http_only())
        self.assertTrue(cookie.is_secure())
        self.assertIsNone(cookie.get_expire_time())


