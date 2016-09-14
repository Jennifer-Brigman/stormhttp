import abc
import asyncio
from .parser import *

__all__ = [
    "AbstractWebSocketProtocol",
    "EchoWebSocketProtocol",
    "SUPPORTED_WEBSOCKET_VERSIONS",
    "WEBSOCKET_SECRET_KEY"
]
SUPPORTED_WEBSOCKET_VERSIONS = {b'13', b'8', b'7'}
WEBSOCKET_SECRET_KEY = b'258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


class AbstractWebSocketProtocol(abc.ABC):
    def __init__(self, server, transport: asyncio.WriteTransport):
        self.server = server
        self.loop = server.loop
        self._message = WebSocketMessage()
        self._parser = WebSocketParser(self._message)
        self._transport = transport

    def data_received(self, data):
        if self._message is None:
            self._message = WebSocketMessage()
            self._parser.set_target(self._message)
        try:
            self._parser.feed_data(data)
        except WebSocketError as error:
            self._transport.write(WebSocketFrame(
                close_code=error.close_code,
                last_frame=1,
                message_code=MESSAGE_CODE_ERROR
            ).to_bytes())
            self._transport.close()

        if self._message.is_message_complete():
            if self._message.message_code == MESSAGE_CODE_PING:
                self._transport.write(WebSocketFrame(last_frame=1, message_code=MESSAGE_CODE_PONG))
            elif self._message.message_code == MESSAGE_CODE_PONG:
                self._transport.write(WebSocketFrame(last_frame=1, message_code=MESSAGE_CODE_PING))
            else:
                self.loop.create_task(self.handle_message(self._message, self._transport))
            self._message = None

    @abc.abstractmethod
    async def handle_message(self, message: WebSocketMessage, transport: asyncio.WriteTransport):
        pass


class EchoWebSocketProtocol(AbstractWebSocketProtocol):
    async def handle_message(self, message: WebSocketMessage, transport: asyncio.WriteTransport):
        transport.write(message.to_bytes())

