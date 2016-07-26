import asyncio
import os
import unittest

import httptools
import jinja2

from stormhttp.web import Application, HTTPRequest, JSONEndPoint

try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


_TEMPLATE_LOADER = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))


def create_http_request(app) -> HTTPRequest:
    request = HTTPRequest()
    request.url = httptools.parse_url(b'/')
    request.method = b'GET'
    request.version = b'1.1'
    request.app = app
    return request


class TestJSONEndpoint(unittest.TestCase):
    def test_simple_json_endpoint(self):
        async def main():
            async def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint(b'/', [b'GET'], JSONEndPoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.body, b'{"a": 0}')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_non_async_json_endpoint(self):
        async def main():
            def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint(b'/', [b'GET'], JSONEndPoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.body, b'{"a": 0}')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_invalid_json_endpoint(self):
        async def main():
            async def handler(request: HTTPRequest):
                return {'a'}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint(b'/', [b'GET'], JSONEndPoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.status_code, 500)

        asyncio.get_event_loop().run_until_complete(main())