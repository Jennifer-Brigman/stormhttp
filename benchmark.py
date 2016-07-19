import asyncio
import stormhttp
import concurrent.futures


class BenchmarkEndPoint(stormhttp.router.AbstractEndPoint):
    def __init__(self, payload):
        self._payload = payload
        self._payload_len = b'%d' % len(self._payload)

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: stormhttp.web.HTTPRequest):
        response = stormhttp.web.HTTPResponse()
        response.body = self._payload
        response.version = request.version
        response.headers[b'Content-Length'] = self._payload_len
        return response


if __name__ == "__main__":
    try:
        import uvloop
        loop = uvloop.new_event_loop()
    except ImportError:
        loop = asyncio.new_event_loop()

    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor())
    app = stormhttp.web.Application(loop)
    app.router.add_endpoint(b'/', {b'GET'}, stormhttp.router.FileEndPoint(__file__))
    stormhttp.web.run_app(app)
