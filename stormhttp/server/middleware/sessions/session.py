__all__ = [
    "Session"
]


class Session(dict):
    def __init__(self, identity, data):
        self.identity = identity
        self._changed = False
        dict.update(self, data)

    @property
    def changed(self) -> bool:
        return self._changed

    def __setitem__(self, key, value):
        old_value = self.get(key)
        if old_value != value and value is not None:
            dict.__setitem__(self, key, value)
            self._changed = True

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._changed = True
