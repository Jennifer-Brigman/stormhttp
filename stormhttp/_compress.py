import brotli
import gzip
import io
import zlib

# Global Variables
__all__ = [
    "encode_bytes",
    "SUPPORTED_ENCODING_TYPES"
]
SUPPORTED_ENCODING_TYPES = {b'identity', b'gzip', b'deflate', b'br'}


def encode_bytes(algorithm: bytes, content: bytes) -> bytes:
    """
    Compresses bytes given an algorithm.
    :param algorithm: Algorithm to compress bytes using.
    :param content: Byte content to compress.
    :return: Compressed bytes.
    """
    if algorithm == b'identity':
        return content
    elif algorithm == b'gzip':
        out = io.BytesIO()
        gzip.GzipFile(fileobj=out, mode="wb").write(content)
        return out.getvalue()
    elif algorithm == b'deflate':
        return zlib.compress(content)[2:-4]
    elif algorithm == b'br':
        return brotli.compress(content)
    else:
        raise ValueError("Compression algorithm: {} is not supported.".format(algorithm))
