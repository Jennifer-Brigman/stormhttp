import sys
import cchardet
from . import fernet

__all__ = [
    "safe_decode"
] + fernet.__all__


def safe_decode(data: bytes) -> str:
    try:
        return data.decode(cchardet.detect(data)["encoding"])
    except UnicodeDecodeError:
        return data.decode(sys.getdefaultencoding())
