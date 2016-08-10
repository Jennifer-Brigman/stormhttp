import asyncio
import unittest
import httptools
from stormhttp.web import Application, HTTPRequest, JSONEndpoint

try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


def create_http_request(app) -> HTTPRequest:
    request = HTTPRequest()
    request.url = httptools.parse_url(b'/')
    request.method = 'GET'
    request.version = '1.1'
    request.app = app
    return request


class TestJSONEndpoint(unittest.TestCase):
    def test_simple_json_endpoint(self):
        async def main():
            async def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint('/', ['GET'], JSONEndpoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.body, '{"a":0}')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_non_async_json_endpoint(self):
        async def main():
            def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint('/', ['GET'], JSONEndpoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.body, '{"a":0}')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_invalid_json_endpoint(self):
        async def main():
            async def handler(request: HTTPRequest):
                return False

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint('/', ['GET'], JSONEndpoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.status_code, 500)

        asyncio.get_event_loop().run_until_complete(main())