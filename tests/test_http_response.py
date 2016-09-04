import unittest


class TestHttpResponse(unittest.TestCase):
    def test_response_create(self):
        from stormhttp.primitives import HttpResponse
        response = HttpResponse()
        response.version = b'1.1'
        response.status = b'OK'
        response.status_code = 200
        response.body = b'test'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\n\r\ntest')

        response.headers[b'Content-Encoding'] = b'gzip'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\nCONTENT-ENCODING: gzip\r\n\r\ntest')

    def test_response_cookies(self):
        from stormhttp.primitives import HttpResponse, HttpCookie
        response = HttpResponse()
        response.version = b'1.1'
        response.status_code = 200
        response.status = b'OK'
        response.body = b'test'

        cookie = HttpCookie()
        cookie.values[b'a'] = b'2'
        response.cookies.add(cookie)

        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\nSET-COOKIE: a=2;\r\n\r\ntest')

    def test_response_parse_cookies(self):
        from stormhttp.primitives import HttpResponse, HttpParser
        import datetime

        response = HttpResponse()
        parser = HttpParser(response)
        parser.feed_data(b'''HTTP/1.1 200 OK\r\nSET-COOKIE: a=1; domain=google.com; path=/; secure; HttpOnly; MaxAge=10; Expires=Thu, 01 Jan 1970 00:00:00 GMT\r\n\r\n''')

        self.assertEqual(len(response.cookies), 1)
        cookie = list(response.cookies.values())[0]
        self.assertEqual(cookie.values[b'a'], b'1')
        self.assertEqual(cookie.domain, b'google.com')
        self.assertEqual(cookie.path, b'/')
        self.assertTrue(cookie.secure)
        self.assertTrue(cookie.http_only)
        self.assertEqual(cookie.max_age, 10)
        self.assertEqual(cookie.expires, datetime.datetime.utcfromtimestamp(0))
