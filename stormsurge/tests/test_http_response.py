import unittest


class TestHTTPResponse(unittest.TestCase):
    def test_create_response(self):
        from stormsurge._http import HTTPResponse
        response = HTTPResponse()
        response.version = b'1.1'
        response.status_code = 200
        response.body = b'test'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\n\r\ntest')

        response.headers[b'Content-Encoding'] = b'gzip'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\ntest')

    def test_cookies_response(self):
        from stormsurge._http import HTTPResponse
        from stormsurge._cookies import HTTPCookies
        response = HTTPResponse()
        response.version = b'1.1'
        response.status_code = 200
        response.body = b'test'
        response.cookies = HTTPCookies(b'a=1;')
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\n\r\ntest')

        response.cookies[b'a'] = b'2'
        self.assertEqual(response.to_bytes(), b'HTTP/1.1 200 OK\r\nSet-Cookie: a=2;\r\n\r\ntest')

    def test_response_invalid_status(self):
        from stormsurge._http import HTTPResponse
        response = HTTPResponse()
        with self.assertRaises(ValueError):
            response.status_code = -1

    def test_response_error_code(self):
        from stormsurge._http import HTTPErrorResponse
        response = HTTPErrorResponse(304)
        self.assertEqual(response.status_code, 304)