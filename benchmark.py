import asyncio
import uvloop
import stormsurge
import concurrent.futures


class BenchmarkEndPoint(stormsurge.router.AbstractEndPoint):
    def __init__(self, payload):
        self._payload = payload
        self._payload_len = b'%d' % len(self._payload)

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: stormsurge.web.HTTPRequest):
        response = stormsurge.web.HTTPResponse()
        response.body = self._payload
        response.version = request.version
        response.headers[b'Content-Length'] = self._payload_len
        return response


if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor())
    app = stormsurge.web.Application(loop)
    app.router.add_endpoint(b'/', {b'GET'}, BenchmarkEndPoint(b'a' * (1024 * 100)))
    stormsurge.web.run_app(app)
