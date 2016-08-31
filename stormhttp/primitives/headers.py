import typing

__all__ = [
    "HttpHeaders"
]


class HttpHeaders(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key: bytes) -> bytes:
        return dict.__getitem__(self, key.upper())

    def __setitem__(self, key: bytes, val: typing.Union[bytes, typing.Iterable[bytes]]) -> None:
        if isinstance(val, bytes):
            val = [val]
        dict.__setitem__(self, key.upper(), val)

    def __delitem__(self, key: bytes) -> None:
        dict.__delitem__(self, key.upper())

    def __contains__(self, key: bytes) -> bool:
        return dict.__contains__(self, key.upper())

    def __repr__(self):
        return dict.__repr__(self)

    def get(self, key, default=None):
        return dict.get(self, key.upper(), default)

    def update(self, *args, **kwargs):
        for key, val in dict(*args, **kwargs).items():
            self[key] = val

    def to_bytes(self) -> bytes:
        return b'\r\n'.join(
            (b'\r\n'.join([b'%b: %b' % (key, val) for val in list_val])) for key, list_val in self.items()
        )
