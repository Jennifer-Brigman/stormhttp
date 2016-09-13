import asyncio
import os
import sys
import struct
import typing

__all__ = [
    "CLOSE_CODE_PROTOCOL_ERROR",

    "WebSocketError",
    "WebSocketFrame",
    "WebSocketParser"
]
CLOSE_CODE_OK = 1000
CLOSE_CODE_GOING_AWAY = 1001
CLOSE_CODE_PROTOCOL_ERROR = 1002
CLOSE_CODE_UNSUPPORTED_DATA = 1003
CLOSE_CODE_INVALID_TEXT = 1007
CLOSE_CODE_POLICY_VIOLATION = 1008
CLOSE_CODE_MESSAGE_TOO_BIG = 1009
CLOSE_CODE_MANDATORY_EXTENSION = 1010
CLOSE_CODE_INTERNAL_ERROR = 1011
CLOSE_CODE_SERVICE_RESTART = 1012
CLOSE_CODE_TRY_AGAIN_LATER = 1013

MESSAGE_CODE_CONTINUE = 0
MESSAGE_CODE_TEXT = 1
MESSAGE_CODE_BINARY = 2
MESSAGE_CODE_CLOSE = 8
MESSAGE_CODE_PING = 9
MESSAGE_CODE_PONG = 10
MESSAGE_CODE_CLOSED = 257
MESSAGE_CODE_ERROR = 258

_BYTE_ORDER = sys.byteorder
_PARSER_STATE_EMPTY = 0
_PARSER_STATE_HEADER = 1
_PARSER_STATE_GET_LENGTH = 2
_PARSER_STATE_MASK = 3
_PARSER_STATE_PAYLOAD = 4


class WebSocketError(Exception):
    def __init__(self, close_code: int, *args, **kwargs):
        self.close_code = close_code
        Exception.__init__(self, *args, **kwargs)
        
        
class WebSocketMessage:
    def __init__(self, message_code: int=0, payload: bytes=b''):
        self.message_code = message_code
        self.payload = payload
        

class WebSocketFrame:
    def __init__(self, last_frame: int=0, message_code: int=0, payload: bytes= b'', close_code: int=-1):
        self.last_frame = last_frame
        self.message_code = message_code
        self.payload = payload
        self.close_code = close_code
        self._is_frame_complete = False

    def __repr__(self):
        return "<WebSocketFrame message_code={} last_frame={} close_code={} payload={}>".format(
            self.message_code, self.last_frame, self.close_code, self.payload
        )

    def on_frame_complete(self):
        self._is_frame_complete = True

    def is_frame_complete(self):
        return self._is_frame_complete


class WebSocketParser:
    def __init__(self, frame: WebSocketFrame=None):
        self._buffer = bytearray()
        self._state = _PARSER_STATE_EMPTY
        self._length = 0
        self._masked = 0
        self._mask = 0
        self._frame = frame

    def _reset(self):
        self._state = _PARSER_STATE_EMPTY
        self._masked = 0

    def set_target(self, frame: WebSocketFrame):
        self._frame = frame

    def feed_data(self, data: bytes):
        self._buffer += data

        # Parsing the WebSocketFrame header
        if self._state == _PARSER_STATE_EMPTY and len(self._buffer) >= 2:

            first_byte, second_byte = self._buffer[:2]
            reserved = first_byte & 112
            if reserved:
                raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received frame with non-zero reserved bits.")

            last_frame = first_byte & 128
            message_code = first_byte & 15

            if message_code > 7 and not last_frame:
                raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received fragmented control frame.")

            self._masked = second_byte & 128
            self._length = second_byte & 127

            if message_code > 7 and self._length > 125:
                raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received a control frame with length greater than 125 bytes.")

            self._frame.message_code = message_code
            self._frame.last_frame = last_frame

            self._state = _PARSER_STATE_HEADER if self._length > 125 else (
                _PARSER_STATE_GET_LENGTH if self._masked else _PARSER_STATE_MASK
            )
            self._buffer = self._buffer[2:]

        # Parsing the WebSocketFrame length (if needed)
        if self._state == _PARSER_STATE_HEADER:
            if self._length == 126 and len(self._buffer) >= 2:
                self._length = struct.unpack("!H", self._buffer[:2])
                self._buffer = self._buffer[2:]
                self._state = _PARSER_STATE_GET_LENGTH

            elif self._length > 126 and len(self._buffer) >= 8:
                self._length = struct.unpack("!Q", self._buffer[:8])[0]
                self._buffer = self._buffer[8:]
                self._state = _PARSER_STATE_GET_LENGTH

        # Parsing the WebSocketFrame mask (if needed)
        if self._state == _PARSER_STATE_GET_LENGTH and len(self._buffer) >= 4:
            self._mask = self._buffer[:4]
            self._buffer = self._buffer[4:]
            self._state = _PARSER_STATE_MASK

        # Parsing the WebSocketFrame payload
        if self._state == _PARSER_STATE_MASK and len(self._buffer) >= self._length:
            if self._frame.message_code == MESSAGE_CODE_CLOSE:
                self._frame.close_code = struct.unpack("!H", self._buffer[:4])
                self._frame.payload = self._frame.payload = self._buffer[4:self._length]
            else:
                self._frame.payload = self._buffer[:self._length]
            self._frame.on_frame_complete()
            self._reset()

async def parse_frame(sock) -> typing.Tuple[int, int, bytes]:
    """
    Parses a frame from a
    :param sock:
    :return:
    """
    first_byte, second_byte = await sock.read(2)
    reserved = first_byte & 112
    if reserved:
        raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received frame with non-zero reserved bits.")

    finished = first_byte & 128
    message_code = first_byte & 15

    if message_code > 7 and not finished:
        raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received fragmented control frame.")

    masked = second_byte & 128
    length = second_byte & 127

    if length == 126:
        length = struct.unpack_from("!H", await sock.read(2))
    elif length > 126:
        length = struct.unpack_from("!Q", await sock.read(8))

    if not length:
        return finished, message_code, bytearray()

    if masked:
        mask = await sock.read(4)
        payload = (
            int.from_bytes(await sock.read(length), _BYTE_ORDER) ^
            (int.from_bytes(mask * (length >> 2) + mask[:length & 3], _BYTE_ORDER))
        ).to_bytes(length, _BYTE_ORDER)
    else:
        payload = await sock.read(length)

    return finished, message_code, payload


def build_frame(message_code: int, payload: bytes) -> bytes:
    length = len(payload)

    if length < 126:
        header = struct.pack("!BB", 128 | message_code, length | 128)
    elif length < 65536:
        header = struct.pack("!BBH", 128 | message_code, 254, length)
    else:
        header = struct.pack("!BBQ", 128 | message_code, 255, length)

    mask = os.urandom(4)
    payload = (
        int.from_bytes(payload, _BYTE_ORDER) ^
        (int.from_bytes(mask * (length >> 2) + mask[:length & 3], _BYTE_ORDER))
    ).to_bytes(length, _BYTE_ORDER)
    return header + mask + payload
