import unittest


class TestHTTPHeaders(unittest.TestCase):
    def test_header_length(self):
        from stormhttp._http import HTTPHeaders
        headers = HTTPHeaders({'a': '1', 'b': '2'})
        self.assertEqual(len(headers), 2)

    def test_header_iter(self):
        from stormhttp._http import HTTPHeaders
        headers = HTTPHeaders({'a': '1', 'b': '2'})
        for key in headers:
            self.assertIn(key, ['a', 'b'])
            self.assertIn(headers[key], ['1', '2'])

    def test_header_contains(self):
        from stormhttp._http import HTTPHeaders
        headers = HTTPHeaders({'a': '1', 'b': '2'})
        self.assertTrue('a' in headers)
        self.assertFalse('1' in headers)

    def test_header_delete(self):
        from stormhttp._http import HTTPHeaders
        headers = HTTPHeaders({'a': '1', 'b': '2'})
        del headers['b']
        self.assertFalse('b' in headers)

    def test_header_key_errors(self):
        from stormhttp._http import HTTPHeaders
        headers = HTTPHeaders({})
        with self.assertRaises(KeyError):
            _ = headers['a']
        with self.assertRaises(KeyError):
            del headers['a']
