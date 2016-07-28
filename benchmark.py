import asyncio
import concurrent.futures
import ssl
import sys
import stormhttp


class BenchmarkEndPoint(stormhttp.web.AbstractEndPoint):
    def __init__(self, payload):
        self._payload = payload
        self._payload_len = str(len(self._payload))

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: stormhttp.web.HTTPRequest):
        response = stormhttp.web.HTTPResponse()
        response.body = self._payload
        response.version = request.version
        response.headers['Content-Length'] = self._payload_len
        return response


if __name__ == "__main__":
    try:
        import uvloop
        loop = uvloop.new_event_loop()
        print("Running with uvloop event loop.")
    except ImportError:
        loop = asyncio.new_event_loop()
        print("Running with asyncio event loop.")
    asyncio.set_event_loop(None)  # Make sure that no structures are relying on asyncio.get_event_loop().

    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor())
    app = stormhttp.web.Application(loop)
<<<<<<< HEAD
    app.router.add_endpoint(b'/', {b'GET'}, BenchmarkEndPoint(b'a' * (1024 * 100)))

    ssl_context = None
    if "--ssl" in sys.argv:
        ssl_context = ssl.create_default_context(cafile="server.crt")
    stormhttp.web.run_app(app, ssl_context=ssl_context)
=======
    app.router.add_endpoint('/', ['GET'], BenchmarkEndPoint('a' * (1024 * 100)))
    stormhttp.web.run_app(app)
>>>>>>> 630d57e6030002e61183ae2ad33975a13e4d97d0
