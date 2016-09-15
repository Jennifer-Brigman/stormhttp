# MIT License
#
# Copyright (c) 2016 Oz N Tiram <oz.tiram@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import binascii
import hmac
import time
import os
import struct
from pyaes import AESModeOfOperationCBC, Encrypter, Decrypter

__all__ = [
    "InvalidSignature",
    "InvalidToken",
    "Fernet"
]
_MAX_CLOCK_SKEW = 60


class InvalidToken(Exception):
    pass


class InvalidSignature(Exception):
    pass


class Fernet:
    def __init__(self, key):
        if not isinstance(key, bytes):
            raise TypeError("key must be bytes.")

        key = base64.urlsafe_b64decode(key)
        if len(key) != 32:
            raise ValueError("Fernet key must be 32 url-safe base64-encoded bytes.")

        self._signing_key = key[:16]
        self._encryption_key = key[16:]

    @classmethod
    def generate_key(cls):
        return base64.urlsafe_b64encode(os.urandom(32))

    def encrypt(self, data) -> bytes:
        current_time = int(time.time())
        iv = os.urandom(16)
        return self._encrypt_from_parts(data, current_time, iv)

    def _encrypt_from_parts(self, data, current_time, iv) -> bytes:
        encrypter = Encrypter(AESModeOfOperationCBC(self._encryption_key, iv))
        ciphertext = encrypter.feed(data)
        ciphertext += encrypter.feed()

        basic_parts = (b"\x80" + struct.pack(">Q", current_time) + iv + ciphertext)

        hmactext = hmac.new(self._signing_key, digestmod='sha256')
        hmactext.update(basic_parts)

        return base64.urlsafe_b64encode(basic_parts + hmactext.digest())

    def decrypt(self, token, ttl=None) -> bytes:
        if not isinstance(token, bytes):
            raise TypeError("token must be bytes.")

        current_time = int(time.time())

        try:
            data = base64.urlsafe_b64decode(token)
        except (TypeError, binascii.Error):
            raise InvalidToken

        if not data or data[0] != 0x80:
            raise InvalidToken

        try:
            timestamp, = struct.unpack(">Q", data[1:9])
        except struct.error:
            raise InvalidToken
        if ttl is not None:
            if timestamp + ttl < current_time:
                raise InvalidToken

            if current_time + _MAX_CLOCK_SKEW < timestamp:
                raise InvalidToken

        hmactext = hmac.new(self._signing_key, digestmod='sha256')
        hmactext.update(data[:-32])
        if not hmac.compare_digest(hmactext.digest(), data[-32:]):
            raise InvalidToken

        iv = data[9:25]
        ciphertext = data[25:-32]
        decryptor = Decrypter(AESModeOfOperationCBC(self._encryption_key, iv))
        try:
            plaintext = decryptor.feed(ciphertext)
            plaintext += decryptor.feed()
        except ValueError:
            raise InvalidToken

        return plaintext
