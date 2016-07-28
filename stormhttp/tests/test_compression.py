import unittest


class TestCompression(unittest.TestCase):
    def test_identity_compression(self):
        from stormhttp._compress import encode_bytes
        self.assertEqual(encode_bytes('identity', b'abc123'), b'abc123')

    def test_gzip_compression(self):
        from stormhttp._compress import encode_bytes
        self.assertEqual(encode_bytes('gzip', b'abc123')[8:],
                         b'\x02\xffKLJ642\x06\x00\\\xbb\x02\xcf\x06\x00\x00\x00')

    def test_deflate_compression(self):
        from stormhttp._compress import encode_bytes
        self.assertEqual(encode_bytes('deflate', b'abc123'),
                         b'KLJ642\x06\x00')

    def test_brotli_compression(self):
        from stormhttp._compress import encode_bytes
        self.assertEqual(encode_bytes('br', b'abc123'),
                         b'\x8b\x02\x80abc123\x03')

    def test_invalid_compression(self):
        from stormhttp._compress import encode_bytes
        with self.assertRaises(ValueError):
            encode_bytes('abc', b'abc123')
