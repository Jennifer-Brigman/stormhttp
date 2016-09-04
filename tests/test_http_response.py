import unittest


class TestHttpResponse(unittest.TestCase):
    def test_create_response(self):
        from stormhttp.primitives import HttpResponse
        response = HttpResponse()
        response.version = b'1.1'
        response.status = b'OK'
        response.status_code = 200
        response.body = b'test'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\n\r\ntest')

        response.headers[b'Content-Encoding'] = b'gzip'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\nCONTENT-ENCODING: gzip\r\n\r\ntest')

    def test_cookies_response(self):
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
