import unittest


class TestHTTPRequest(unittest.TestCase):
    def test_create_request(self):
        import stormsurge.http
        request = stormsurge.http.HTTPRequest()
        request.on_url(b'/')
        request.version = b'1.1'
        request.method = b'GET'
        request.headers[b'Host'] = b'localhost'
        request.body = b'test'

        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\nHost: localhost\r\n\r\ntest')
