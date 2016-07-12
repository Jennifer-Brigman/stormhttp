import unittest


class TestCompression(unittest.TestCase):
    def test_compression_methods(self):
        import stormsurge.http.compress
        original_bytes = b'abc' * 1024
        self.assertEqual(stormsurge.http.compress.compress_bytes(b'identity', original_bytes), original_bytes)
        self.assertLess(len(stormsurge.http.compress.compress_bytes(b'gzip', original_bytes)), len(original_bytes))
        self.assertLess(len(stormsurge.http.compress.compress_bytes(b'br', original_bytes)), len(original_bytes))
        self.assertLess(len(stormsurge.http.compress.compress_bytes(b'deflate', original_bytes)), len(original_bytes))