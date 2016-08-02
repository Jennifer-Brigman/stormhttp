import re
import cchardet

# Globals
__all__ = [
    "safe_decode",
    "parse_url_escapes"
]
_URL_ESCAPE_REGEX = re.compile(r"((?:%[0-9a-fA-F]{2})+)")


def safe_decode(message: bytes) -> str:
    """
    Safely decodes bytes into a string by determining encoding.
    :param message: Bytes to decode.
    :return: String after decoding.
    """
    encoding = cchardet.detect(message).get("encoding", "")
    if encoding != "":
        return message.decode(encoding)
    return message.decode("utf-8")


def parse_url_escapes(url: str) -> str:
    """
    Parses all URL escapes in a URL into their correct character.
    This makes supporting all of UTF-8 valid in headers.
    :param url: URL to parse.
    :return: Parsed URL.
    """
    escapes = {}
    for escape in _URL_ESCAPE_REGEX.findall(url):
        if escape not in escapes:
            escapes[escape] = safe_decode(bytearray.fromhex(escape.replace("%", "")))
    for escape in escapes:
        url = url.replace(escape, escapes[escape])
    return url
