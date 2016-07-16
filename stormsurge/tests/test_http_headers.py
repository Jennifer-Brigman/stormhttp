import unittest


class TestHTTPHeaders(unittest.TestCase):
    def test_header_length(self):
        from stormsurge._http import HTTPHeaders
        headers = HTTPHeaders({b'a': b'1', b'b': b'2'})
        self.assertEqual(len(headers), 2)

    def test_header_iter(self):
        from stormsurge._http import HTTPHeaders
        headers = HTTPHeaders({b'a': b'1', b'b': b'2'})
        for key in headers:
            self.assertIn(key, [b'a', b'b'])
            self.assertIn(headers[key], [b'1', b'2'])

    def test_header_contains(self):
        from stormsurge._http import HTTPHeaders
        headers = HTTPHeaders({b'a': b'1', b'b': b'2'})
        self.assertTrue(b'a' in headers)
        self.assertFalse(b'1' in headers)

    def test_header_delete(self):
        from stormsurge._http import HTTPHeaders
        headers = HTTPHeaders({b'a': b'1', b'b': b'2'})
        del headers[b'b']
        self.assertFalse(b'b' in headers)

    def test_header_key_errors(self):
        from stormsurge._http import HTTPHeaders
        headers = HTTPHeaders({})
        with self.assertRaises(KeyError):
            _ = headers[b'a']
        with self.assertRaises(KeyError):
            del headers[b'a']
