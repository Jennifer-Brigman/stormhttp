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
        self._sent_close = False

    def data_received(self, data):
        if self._message is None:
            self._message = WebSocketMessage()
            self._parser.set_target(self._message)
        try:
            self._parser.feed_data(data)
        except WebSocketError as error:
            self.close(error.close_code)

        if self._message.is_message_complete():

            # Response to PING messages with a PONG.
            if self._message.message_code == MESSAGE_CODE_PING:
                self._transport.write(WebSocketMessage(message_code=MESSAGE_CODE_PONG, payload=self._message.payload).to_bytes())

            # Unsolicited PONG message should be ignored.
            elif self._message.message_code == MESSAGE_CODE_PONG:
                pass

            elif self._message.message_code == MESSAGE_CODE_CLOSE:
                # If our Transport is already closing, then it must have been us that initiated.
                self.close()

            # If our Transport is closing, then don't send any more messages.
            elif not self._transport.is_closing():
                self.loop.create_task(self.handle_message(self._message, self._transport))

            self._message = None

    def close(self, close_code: int=CLOSE_CODE_PROTOCOL_ERROR):
        if not self._transport.is_closing():
            if not self._sent_close:
                self._sent_close = True
                self._transport.write(WebSocketMessage(message_code=MESSAGE_CODE_CLOSE, close_code=close_code))
            self._transport.close()

    @abc.abstractmethod
    async def handle_message(self, message: WebSocketMessage, transport: asyncio.WriteTransport):
        pass


class EchoWebSocketProtocol(AbstractWebSocketProtocol):
    async def handle_message(self, message: WebSocketMessage, transport: asyncio.WriteTransport):
        transport.write(message.to_bytes())

