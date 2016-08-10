import asyncio
import os
import unittest
import httptools
from stormhttp.web import Application, HTTPRequest, FileEndpoint

try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass

_VIRTUAL_DIRECTORY = os.path.join(os.path.dirname(__file__), "virtual_files")


def create_http_request(app, url) -> HTTPRequest:
    request = HTTPRequest()
    request.url = httptools.parse_url(url)
    request.url_bytes = url.decode("utf-8")
    request.method = 'GET'
    request.version = '1.1'
    request.app = app
    request.body = ""
    return request


class TestFileEndpoint(unittest.TestCase):
    def test_simple_file_endpoint(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint("/hello.txt", ["GET"], FileEndpoint(os.path.join(_VIRTUAL_DIRECTORY, "hello.txt")))
            response = await app.router.route_request(create_http_request(app, b'/hello.txt'))
            self.assertEqual(response.body, b'Hello, world!')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_valid_etag_cache_file_endpoint(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint("/hello.txt", ["GET"], FileEndpoint(os.path.join(_VIRTUAL_DIRECTORY, "hello.txt")))
            response = await app.router.route_request(create_http_request(app, b'/hello.txt'))
            etag = response.headers["ETag"]

            request = create_http_request(app, b'/hello.txt')
            request.headers["If-None-Match"] = etag
            response = await app.router.route_request(request)
            self.assertEqual(response.status_code, 304)
            self.assertEqual(len(response.body), 0)

        asyncio.get_event_loop().run_until_complete(main())

    def test_invalid_etag_cache_file_endpoint(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint("/hello.txt", ["GET"], FileEndpoint(os.path.join(_VIRTUAL_DIRECTORY, "hello.txt")))
            response = await app.router.route_request(create_http_request(app, b'/hello.txt'))
            etag = response.headers["ETag"]

            request = create_http_request(app, b'/hello.txt')
            request.headers["If-None-Match"] = etag + "1"
            response = await app.router.route_request(request)
            app.router.route_request(request)
            self.assertEqual(response.body, b'Hello, world!')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["ETag"], etag)

        asyncio.get_event_loop().run_until_complete(main())