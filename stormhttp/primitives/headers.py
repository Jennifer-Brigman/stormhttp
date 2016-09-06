import re
import typing

__all__ = [
    "HttpHeaders"
]
_QLIST_REGEX = re.compile(b'\s?([^,;]+)(?:;q=(\\-?[\\d\\.]+))?(?:,\s?|$)')
_HTTP_HEADER_FORMAT_STRING = b'%b: %b'
_HTTP_HEADER_SEPARATOR = b'\r\n'
# text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
# r.findall(b'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')

class HttpHeaders(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key: bytes) -> bytes:
        return dict.__getitem__(self, key.upper())

    def __setitem__(self, key: bytes, val: typing.Union[bytes, typing.Iterable[bytes]]) -> None:
        if isinstance(val, int):
            val = [b'%d' % val]
        if isinstance(val, bytes):
            val = [val]
        dict.__setitem__(self, key.upper(), val)

    def __delitem__(self, key: bytes) -> None:
        dict.__delitem__(self, key.upper())

    def __contains__(self, key: bytes) -> bool:
        return dict.__contains__(self, key.upper())

    def __repr__(self):
        return "<HttpHeaders {}>".format(" ".join(["{}={}".format(key, val) for key, val in self.items()]))

    def get(self, key: bytes, default=None) -> typing.Union[None, typing.Iterable[bytes]]:
        return dict.get(self, key.upper(), default)

    def update(self, *args, **kwargs):
        for key, val in dict(*args, **kwargs).items():
            self[key] = val

    def qlist(self, key: bytes) -> typing.List[typing.Tuple[float, bytes]]:
        """
        Sorts a header into a list according to it's q-values.
        Items without q-values are valued highest.
        :param key: Header to get the qlist for.
        :return: List of items with their qvalue and their byte data sorted highest to lowest.
        """
        header = self.get(key)
        if header is None:
            raise KeyError(str(key))
        qlist = _QLIST_REGEX.findall(b','.join(header))
        for i in range(len(qlist)):
            item, qvalue = qlist[i]
            if qvalue == b'':
                qlist[i] = (1.0, item)
            else:
                qlist[i] = (float(qvalue.decode("ascii")), item)
        return sorted(qlist, key=lambda k: k[0], reverse=True)

    def to_bytes(self) -> bytes:
        return _HTTP_HEADER_SEPARATOR.join((
            _HTTP_HEADER_SEPARATOR.join([_HTTP_HEADER_FORMAT_STRING % (key, val) for val in list_val])
        ) for key, list_val in self.items())
