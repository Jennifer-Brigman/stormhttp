import unittest


class TestHTTPRequest(unittest.TestCase):
    def test_create_request(self):
        from stormhttp._http import HTTPRequest
        request = HTTPRequest()

        request.version = '1.1'
        request.method = 'GET'
        request.url_bytes = '/'
        request.body = 'test'
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\n\r\ntest')

        request.headers['Accept'] = 'text/html'
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\nAccept: text/html\r\n\r\ntest')

        request.headers['Accept-Encoding'] = 'utf-8'
        self.assertIn(request.to_bytes(), [
            b'GET / HTTP/1.1\r\nAccept: text/html\r\nAccept-Encoding: utf-8\r\n\r\ntest',
            b'GET / HTTP/1.1\r\nAccept-Encoding: utf-8\r\nAccept: text/html\r\n\r\ntest'
        ])

    def test_parse_cookie_first(self):
        from stormhttp._http import HTTPRequest
        import httptools
        data = b'GET / HTTP/1.1\r\nAccept: text/html\r\nCookie: a=1;\r\n\r\n'
        request = HTTPRequest()
        parser = httptools.HttpRequestParser(request)
        parser.feed_data(data)
        request.version = parser.get_http_version()
        request.method = parser.get_method().decode("utf-8")
        self.assertTrue('a' in request.cookies)
        self.assertEqual(request.cookies.get('a', None), '1')

        self.assertIn(request.to_bytes(), [
            b'GET / HTTP/1.1\r\nAccept: text/html\r\nCookie: a=1;\r\n\r\n',
            b'GET / HTTP/1.1\r\nCookie: a=1;\r\nAccept: text/html\r\n\r\n'
        ])

    def test_http_parser(self):
        from stormhttp._http import HTTPRequest
        import httptools

        data = b'GET / HTTP/1.1\r\nAccept: text/html\r\nAccept-Encoding: utf-8\r\nCookie: a=1;\r\n\r\n'
        for block_size in range(1, len(data)+1):
            index = 0
            request = HTTPRequest()
            parser = httptools.HttpRequestParser(request)
            self.assertFalse(request.is_complete())

            while index < len(data):
                if index + block_size >= len(data):
                    data_block = data[index:]
                else:
                    data_block = data[index:index+block_size]

                index += len(data_block)
                parser.feed_data(data_block)

            request.method = parser.get_method().decode("utf-8")
            request.version = parser.get_http_version()
            self.assertTrue(request.is_complete())
            self.assertEqual(request.method, 'GET')
            self.assertEqual(request.version, '1.1')
            self.assertEqual(request.url_bytes, '/')
            self.assertEqual(request.headers.get('Accept', None), 'text/html')
            self.assertEqual(request.headers.get('Accept-Encoding', None), 'utf-8')
            self.assertEqual(request.cookies.get('a', None), '1')
