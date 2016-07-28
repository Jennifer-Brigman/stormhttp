import brotli
import gzip
import io
import zlib

# Global Variables
__all__ = [
    "encode_bytes",
    "SUPPORTED_ENCODING_TYPES"
]
SUPPORTED_ENCODING_TYPES = {'identity', 'gzip', 'deflate', 'br'}


def encode_bytes(algorithm: str, content: bytes) -> bytes:
    """
    Compresses bytes given an algorithm.
    :param algorithm: Algorithm to compress bytes using.
    :param content: Byte content to compress.
    :return: Compressed bytes.
    """
    if algorithm == 'identity':
        return content
    elif algorithm == 'gzip':
        out = io.BytesIO()
        gzip.GzipFile(fileobj=out, mode="wb").write(content)
        return out.getvalue()
    elif algorithm == 'deflate':
        return zlib.compress(content)[2:-4]
    elif algorithm == 'br':
        return brotli.compress(content)
    else:
        raise ValueError("Compression algorithm: {} is not supported.".format(algorithm))
