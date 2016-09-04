import unittest


class TestHttpRequest(unittest.TestCase):
    def test_create_request(self):
        from stormhttp.primitives import HttpRequest, HttpUrl
        request = HttpRequest()

        request.version = b'1.1'
        request.method = b'GET'
        request.url = HttpUrl(b'/', b'', b'', 0, b'', b'', b'', b'')
        request.body = b'test'
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\n\r\ntest')

        request.headers[b'Accept'] = b'text/html'
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\nACCEPT: text/html\r\n\r\ntest')

        request.headers[b'Accept-Encoding'] = b'utf-8'
        self.assertIn(request.to_bytes(), [
            b'GET / HTTP/1.1\r\nACCEPT: text/html\r\nACCEPT-ENCODING: utf-8\r\n\r\ntest',
            b'GET / HTTP/1.1\r\nACCEPT-ENCODING: utf-8\r\nACCEPT: text/html\r\n\r\ntest'
        ])

    def test_parse_cookie_first(self):
        from stormhttp.primitives import HttpRequest, HttpParser

        data = b'GET / HTTP/1.1\r\nCookie: a=1;\r\n\r\n'
        request = HttpRequest()
        parser = HttpParser(request)
        parser.feed_data(data)
        self.assertEqual(len(request.cookies), 1)
        self.assertEqual(list(request.cookies.values())[0].values[b'a'], b'1')
        self.assertEqual(request.to_bytes(), b'GET / HTTP/1.1\r\nCOOKIE: a=1;\r\n\r\n')

    def test_http_parser(self):
        from stormhttp.primitives import HttpRequest, HttpParser

        data = b'GET / HTTP/1.1\r\nACCEPT: text/html\r\nACCEPT-ENCODING: utf-8\r\n\r\n'
        for block_size in range(1, len(data)+1):
            index = 0
            request = HttpRequest()
            parser = HttpParser(request)

            while index < len(data):
                if index + block_size >= len(data):
                    data_block = data[index:]
                else:
                    data_block = data[index:index+block_size]

                index += len(data_block)
                parser.feed_data(data_block)

            self.assertEqual(request.method, b'GET')
            self.assertEqual(request.version, b'1.1')
            self.assertEqual(request.url.raw, b'/')
            self.assertEqual(request.headers.get(b'Accept', None), [b'text/html'])
            self.assertEqual(request.headers.get(b'Accept-Encoding', None), [b'utf-8'])

    def test_http_multiple_headers(self):
        from stormhttp.primitives import HttpRequest, HttpParser

        data = b'GET / HTTP/1.1\r\nACCEPT: text/html\r\nACCEPT: application/json\r\n\r\n'
        request = HttpRequest()
        parser = HttpParser(request)
        parser.feed_data(data)
        self.assertEqual(request.headers.get(b'Accept', None), [b'text/html', b'application/json'])
