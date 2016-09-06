import unittest


class TestHttpHeaders(unittest.TestCase):
    def test_headers_bytes(self):
        from stormhttp.primitives import HttpHeaders
        headers = HttpHeaders()
        headers[b'a'] = b'b'
        self.assertEqual(headers[b'a'], [b'b'])

    def test_headers_list_of_bytes(self):
        from stormhttp.primitives import HttpHeaders
        headers = HttpHeaders()
        headers[b'a'] = [b'b']
        self.assertEqual(headers[b'a'], [b'b'])

    def test_headers_int(self):
        from stormhttp.primitives import HttpHeaders
        headers = HttpHeaders()
        headers[b'a'] = 1
        self.assertEqual(headers[b'a'], [b'1'])

    def test_headers_multiple(self):
        from stormhttp.primitives import HttpHeaders

        headers = HttpHeaders()
        headers[b'a'] = [b'1', b'2', b'3']
        self.assertEqual(headers[b'a'], [b'1', b'2', b'3'])
        self.assertEqual(headers.to_bytes(), b'A: 1\r\nA: 2\r\nA: 3')
