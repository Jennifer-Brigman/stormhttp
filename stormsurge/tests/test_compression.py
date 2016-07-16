import unittest


class TestCompression(unittest.TestCase):
    def test_identity_compression(self):
        from stormsurge._compress import compress_bytes
        self.assertEqual(compress_bytes(b'identity', b'abc123'), b'abc123')

    def test_gzip_compression(self):
        from stormsurge._compress import compress_bytes
        self.assertEqual(compress_bytes(b'gzip', b'abc123')[8:],
                         b'\x02\xffKLJ642\x06\x00\\\xbb\x02\xcf\x06\x00\x00\x00')

    def test_deflate_compression(self):
        from stormsurge._compress import compress_bytes
        self.assertEqual(compress_bytes(b'deflate', b'abc123'),
                         b'KLJ642\x06\x00')

    def test_brotli_compression(self):
        from stormsurge._compress import compress_bytes
        self.assertEqual(compress_bytes(b'br', b'abc123'),
                         b'\x8b\x02\x80abc123\x03')

    def test_invalid_compression(self):
        from stormsurge._compress import compress_bytes
        with self.assertRaises(ValueError):
            compress_bytes(b'abc', b'abc123')
