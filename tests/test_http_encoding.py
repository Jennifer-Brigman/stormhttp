import unittest


class TestHttpEncodings(unittest.TestCase):
    def test_encoding_brotli(self):
        from stormhttp import HttpResponse
        response = HttpResponse()

        original_body = b'abc' * 10
        response.body = original_body
        self.assertEqual(response.body, original_body)

        response.set_encoding(b'br')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'br'])
        self.assertEqual(response.body, b'\x1b\x1d\x00\x00$\xc3\xc4\xc6\x82\x9b \xaa\x01')

        response.set_encoding(b'identity')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'identity'])
        self.assertEqual(response.headers[b'Content-Length'], [b'%d' % len(original_body)])
        self.assertEqual(response.body, original_body)

    def test_encoding_deflate(self):
        from stormhttp import HttpResponse
        response = HttpResponse()

        original_body = b'abc' * 10
        response.body = original_body
        self.assertEqual(response.body, original_body)

        response.set_encoding(b'deflate')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'deflate'])
        self.assertEqual(response.body, b'KLJN\xc4\x8d\x00')

        response.set_encoding(b'identity')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'identity'])
        self.assertEqual(response.headers[b'Content-Length'], [b'%d' % len(original_body)])
        self.assertEqual(response.body, original_body)

    def test_encoding_gzip(self):
        from stormhttp import HttpResponse
        response = HttpResponse()

        original_body = b'abc' * 10
        response.body = original_body
        self.assertEqual(response.body, original_body)

        response.set_encoding(b'gzip')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'gzip'])
        self.assertEqual(response.body[10:], b'KLJN\xc4\x8d\x00\x81\xfc\xb1H\x1e\x00\x00\x00')

        response.set_encoding(b'identity')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'identity'])
        self.assertEqual(response.headers[b'Content-Length'], [b'%d' % len(original_body)])
        self.assertEqual(response.body, original_body)

    def test_encoding_reencode(self):
        from stormhttp import HttpResponse

        response = HttpResponse()

        original_body = b'abc' * 10
        response.body = original_body
        self.assertEqual(response.body, original_body)

        response.set_encoding(b'gzip')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'gzip'])
        self.assertEqual(response.body[10:], b'KLJN\xc4\x8d\x00\x81\xfc\xb1H\x1e\x00\x00\x00')

        response.set_encoding(b'deflate')
        self.assertEqual(response.headers[b'Content-Encoding'], [b'deflate'])
        self.assertEqual(response.body, b'KLJN\xc4\x8d\x00')