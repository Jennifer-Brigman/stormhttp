import unittest


class TestHTTPRequest(unittest.TestCase):
    def test_create_request(self):
        from stormsurge._http import HTTPRequest
        request = HTTPRequest()

        request.version = b'1.1'
        request.method = b'GET'
        request.url_bytes = b'/'
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\n\r\n')

        request.headers[b'Accept'] = b'text/html'
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\nAccept: text/html\r\n\r\n')

        request.headers[b'Accept-Encoding'] = b'utf-8'
        self.assertIn(request.to_bytes(), [
            b'GET / HTTP/1.1\r\nAccept: text/html\r\nAccept-Encoding: utf-8\r\n\r\n',
            b'GET / HTTP/1.1\r\nAccept-Encoding: utf-8\r\nAccept: text/html\r\n\r\n'
        ])

    def test_http_parser(self):
        from stormsurge._http import HTTPRequest
        import httptools

        data = b'GET / HTTP/1.1\r\nAccept: text/html\r\nAccept-Encoding: utf-8\r\nCookie: a=1;\r\n\r\n'
        for block_size in range(1, len(data)+1):
            index = 0
            request = HTTPRequest()
            parser = httptools.HttpRequestParser(request)
            self.assertFalse(request.is_complete())

            while index < len(data):
                if index + block_size < len(data):
                    data_block = data[index:]
                else:
                    data_block = data[index:index+block_size]
                index += len(data_block)
                parser.feed_data(data_block)
                request.method = parser.get_method()
                request.version = parser.get_http_version().encode("latin-1")
                self.assertTrue(request.is_complete())
                self.assertEqual(request.method, b'GET')
                self.assertEqual(request.version, b'1.1')
                self.assertEqual(request.url_bytes, b'/')
                self.assertEqual(request.headers.get(b'Accept', None), b'text/html')
                self.assertEqual(request.headers.get(b'Accept-Encoding', None), b'utf-8')
                self.assertEqual(request.cookies.get(b'a', None), b'1')
