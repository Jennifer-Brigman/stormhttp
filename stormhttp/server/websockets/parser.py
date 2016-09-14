import asyncio
import os
import sys
import struct
import typing

__all__ = [
    "CLOSE_CODE_PROTOCOL_ERROR",

    "MESSAGE_CODE_CONTINUE",
    "MESSAGE_CODE_TEXT",
    "MESSAGE_CODE_BINARY",
    "MESSAGE_CODE_CLOSE",
    "MESSAGE_CODE_PING",
    "MESSAGE_CODE_PONG",
    "MESSAGE_CODE_CLOSED",
    "MESSAGE_CODE_ERROR",

    "WebSocketError",
    "WebSocketFrame",
    "WebSocketMessage",
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
_MAX_LENGTH_PER_FRAME = 0xFFFFFFFFFFFFFFFF


class WebSocketError(Exception):
    def __init__(self, close_code: int, *args, **kwargs):
        self.close_code = close_code
        Exception.__init__(self, *args, **kwargs)
        
        
class WebSocketMessage:
    def __init__(self, message_code: int=0, close_code: int=-1, payload: bytes=b''):
        self.message_code = message_code
        self.close_code = close_code
        self.payload = payload
        self.frames = []  # type: typing.List[WebSocketFrame]
        self._is_message_complete = False

    def __repr__(self):
        return "<WebSocketMessage message_code={} close_code={} payload={}>".format(
            self.message_code, self.close_code, self.payload
        )

    def is_message_complete(self) -> bool:
        return self._is_message_complete

    def on_message_complete(self):
        self._is_message_complete = True
        self.message_code = self.frames[-1].message_code
        self.close_code = self.frames[0].close_code
        self.payload = b''.join([frame.payload for frame in self.frames])

    def to_bytes(self):
        self.to_frames()
        return b''.join([frame.to_bytes() for frame in self.frames])

    def to_frames(self):
        if self.frames:
            self.frames = []
        payload_length = len(self.payload)
        if payload_length > _MAX_LENGTH_PER_FRAME:
            for i in range(len(self.payload) // _MAX_LENGTH_PER_FRAME):
                next_frame = WebSocketFrame(
                    last_frame=0,
                    message_code=MESSAGE_CODE_CONTINUE,
                    payload=self.payload[(i * _MAX_LENGTH_PER_FRAME):((i + 1) * _MAX_LENGTH_PER_FRAME)]
                )
                if i == 0 and self.close_code > 0:
                    next_frame.close_code = self.close_code
                self.frames.append(next_frame)
            payload_length %= _MAX_LENGTH_PER_FRAME
        frames_length = len(self.frames)
        last_frame = WebSocketFrame(
            last_frame=1,
            message_code=self.message_code,
            payload=self.payload[(_MAX_LENGTH_PER_FRAME * frames_length):],
            close_code=self.close_code if self.close_code > 0 and frames_length else -1
        )
        self.frames.append(last_frame)


class WebSocketFrame:
    def __init__(self, last_frame: int=0, message_code: int=0, payload: bytes=b'', close_code: int=-1):
        self.last_frame = last_frame
        self.message_code = message_code
        self.payload = payload  # type: bytes
        self.close_code = close_code

    def __repr__(self):
        return "<WebSocketFrame message_code={} last_frame={} close_code={} payload={}>".format(
            self.message_code, self.last_frame, self.close_code, self.payload
        )

    def to_bytes(self) -> bytes:
        length = len(self.payload)

        if length < 126:
            header = struct.pack("!BB", (self.last_frame << 7) | self.message_code, length | 128)
        elif length < 65536:
            header = struct.pack("!BBH", (self.last_frame << 7) | self.message_code, 254, length)
        else:
            header = struct.pack("!BBQ", (self.last_frame << 7) | self.message_code, 255, length)

        mask = b'\x00' * 4
        payload = self.payload
        if self.close_code > 0:
            payload = struct.pack("!H", self.close_code) + payload
        payload = (
            int.from_bytes(payload, _BYTE_ORDER) ^
            (int.from_bytes(mask * (length >> 2) + mask[:length & 3], _BYTE_ORDER))
        ).to_bytes(length, _BYTE_ORDER)

        return header + mask + payload


class WebSocketParser:
    def __init__(self, message: WebSocketMessage=None):
        self._buffer = bytearray()
        self._state = _PARSER_STATE_EMPTY
        self._length = 0
        self._masked = 0
        self._mask = 0
        self._frame = WebSocketFrame()
        self._message = message

    def _reset(self):
        self._state = _PARSER_STATE_EMPTY
        self._masked = 0
        self._frame = WebSocketFrame()

    def set_target(self, message: WebSocketMessage):
        self._message = message

    def feed_data(self, data: bytes):
        self._buffer += data
        buffer_length = len(self._buffer)

        # Parsing the WebSocketFrame header
        if self._state == _PARSER_STATE_EMPTY and buffer_length >= 2:

            first_byte, second_byte = self._buffer[:2]
            reserved = first_byte & 14
            if reserved:
                raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received frame with non-zero reserved bits.")

            last_frame = first_byte & 0x80
            message_code = first_byte & 0x7F

            if message_code > 7 and not last_frame:
                raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received fragmented control frame.")

            self._masked = second_byte & 128
            self._length = second_byte & 127

            if message_code > 7 and self._length > 125:
                raise WebSocketError(CLOSE_CODE_PROTOCOL_ERROR, "Received a control frame with length greater than 125 bytes.")

            self._frame.message_code = message_code
            self._frame.last_frame = 1 if last_frame else 0

            self._state = _PARSER_STATE_HEADER if self._length > 125 else (
                _PARSER_STATE_GET_LENGTH if self._masked else _PARSER_STATE_MASK
            )
            self._buffer = self._buffer[2:]
            buffer_length -= 2

        # Parsing the WebSocketFrame length (if needed)
        if self._state == _PARSER_STATE_HEADER:
            if self._length == 126 and buffer_length >= 2:
                self._length = struct.unpack("!H", self._buffer[:2])
                self._state = _PARSER_STATE_GET_LENGTH
                self._buffer = self._buffer[2:]
                buffer_length -= 2

            elif self._length > 126 and buffer_length >= 8:
                self._length = struct.unpack("!Q", self._buffer[:8])[0]
                self._state = _PARSER_STATE_GET_LENGTH
                self._buffer = self._buffer[8:]
                buffer_length -= 8

        # Parsing the WebSocketFrame mask (if needed)
        if self._state == _PARSER_STATE_GET_LENGTH and buffer_length >= 4:
            self._mask = self._buffer[:4]
            self._state = _PARSER_STATE_MASK
            self._buffer = self._buffer[4:]
            buffer_length -= 4

        # Parsing the WebSocketFrame payload
        if self._state == _PARSER_STATE_MASK and buffer_length >= self._length:
            if self._frame.message_code == MESSAGE_CODE_CLOSE:
                self._frame.close_code = struct.unpack("!H", self._buffer[:2])[0]
                self._frame.payload = bytes(self._buffer[2:self._length])
            else:
                self._frame.payload = bytes(self._buffer[:self._length])
            if self._masked:
                self._frame.payload = (
                    int.from_bytes(self._frame.payload, _BYTE_ORDER) ^
                    (int.from_bytes(self._mask * (self._length >> 2) + self._mask[:self._length & 3], _BYTE_ORDER))
                ).to_bytes(self._length, _BYTE_ORDER)
            self._message.frames.append(self._frame)
            self._buffer = self._buffer[self._length:]
            if self._frame.last_frame:
                self._message.on_message_complete()

            self._reset()
