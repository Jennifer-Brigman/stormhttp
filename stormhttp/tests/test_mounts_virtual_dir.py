import asyncio
import os
import unittest
import httptools
from stormhttp.web import Application, HTTPRequest, VirtualDirectoryMount

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


class TestVirtualDirectoryMount(unittest.TestCase):
    def test_simple_virtual_dir_mount(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_mount("/test", VirtualDirectoryMount(_VIRTUAL_DIRECTORY))
            response = await app.router.route_request(create_http_request(app, b'/test/hello.txt'))
            self.assertEqual(response.body, b'Hello, world!')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_found_virtual_dir_mount(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_mount("/test", VirtualDirectoryMount(_VIRTUAL_DIRECTORY))
            response = await app.router.route_request(create_http_request(app, b'/test/hello2.txt'))
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_subpath_virtual_dir_mount(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_mount("/test", VirtualDirectoryMount(_VIRTUAL_DIRECTORY))
            response = await app.router.route_request(create_http_request(app, b'/test/../hello2.txt'))
            self.assertEqual(response.status_code, 403)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_subpath2_virtual_dir_mount(self):
        async def main():
            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_mount("/test", VirtualDirectoryMount(_VIRTUAL_DIRECTORY))
            response = await app.router.route_request(create_http_request(app, b'/test/../test/hello2.txt'))
            self.assertEqual(response.status_code, 403)

        asyncio.get_event_loop().run_until_complete(main())