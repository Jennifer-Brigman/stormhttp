import unittest


class TestHttpHeaders(unittest.TestCase):
    def test_headers_bytes(self):
        from stormhttp import HttpHeaders
        headers = HttpHeaders()
        headers[b'a'] = b'b'
        self.assertEqual(headers[b'a'], [b'b'])

    def test_headers_list_of_bytes(self):
        from stormhttp import HttpHeaders
        headers = HttpHeaders()
        headers[b'a'] = [b'b']
        self.assertEqual(headers[b'a'], [b'b'])

    def test_headers_int(self):
        from stormhttp import HttpHeaders
        headers = HttpHeaders()
        headers[b'a'] = 1
        self.assertEqual(headers[b'a'], [b'1'])

    def test_headers_multiple(self):
        from stormhttp import HttpHeaders

        headers = HttpHeaders()
        headers[b'a'] = [b'1', b'2', b'3']
        self.assertEqual(headers[b'a'], [b'1', b'2', b'3'])
        self.assertEqual(headers.to_bytes(), b'A: 1\r\nA: 2\r\nA: 3')

    def test_headers_qlist_no_qvalues(self):
        from stormhttp import HttpHeaders

        headers = HttpHeaders()
        headers[b'Accept-Encoding'] = b'gzip, deflate, br'
        self.assertEqual(headers.qlist(b'Accept-Encoding'), [(b'gzip', 1.0), (b'deflate', 1.0), (b'br', 1.0)])

    def test_headers_qlist_only_qvalues(self):
        from stormhttp import HttpHeaders

        headers = HttpHeaders()
        headers[b'Accept'] = b'*/*;q=0.8,application/xml;q=0.9'
        self.assertEqual(headers.qlist(b'Accept'), [(b'application/xml', 0.9), (b'*/*', 0.8)])

    def test_headers_qlist_mixed_qvalues(self):
        from stormhttp import HttpHeaders

        headers = HttpHeaders()
        headers[b'Accept'] = b'application/xml;q=0.9,text/html,*/*;q=0.8'
        self.assertEqual(headers.qlist(b'Accept'), [(b'text/html', 1.0), (b'application/xml', 0.9), (b'*/*', 0.8)])
