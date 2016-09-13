import sys
import cchardet


def safe_decode(data: bytes) -> str:
    try:
        return data.decode(cchardet.detect(data)["encoding"])
    except UnicodeDecodeError:
        return data.decode(sys.getdefaultencoding())
