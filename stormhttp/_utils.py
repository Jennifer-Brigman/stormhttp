import cchardet


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
