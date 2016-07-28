import asyncio
import httptools
import unittest
from stormhttp.web import Application, HTTPRequest, HTTPResponse, EndPoint
import stormhttp.ext.session


def create_http_request(app) -> HTTPRequest:
    request = HTTPRequest()
    request.url = httptools.parse_url(b'/')
    request.method = 'GET'
    request.version = '1.1'
    request.app = app
    return request


class TestSession(unittest.TestCase):
    def test_add_simple_ession(self):
        async def main():
            async def handler(request: HTTPRequest):
                self.assertTrue(hasattr(request, "session"))

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.session.setup(app, stormhttp.ext.session.SimpleStorage())
            app.router.add_endpoint('/', ['GET'], EndPoint(handler))
            await app.router.route_request(create_http_request(app))

        asyncio.get_event_loop().run_until_complete(main())

    def test_save_simple_session(self):
        async def main():
            async def handler(request: HTTPRequest):
                self.assertTrue(hasattr(request, "session"))
                return request.decorate_response(HTTPResponse())

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.session.setup(app, stormhttp.ext.session.SimpleStorage())
            app.router.add_endpoint('/', ['GET'], EndPoint(handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertTrue('_stormhttp_session' in response.cookies)
            self.assertEqual(response.cookies['_stormhttp_session'], '{}')

        asyncio.get_event_loop().run_until_complete(main())

    def test_load_simple_session(self):
        async def main():
            async def handler(request: HTTPRequest):
                self.assertEqual(request.session["a"], 1)
                return request.decorate_response(HTTPResponse())

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.session.setup(app, stormhttp.ext.session.SimpleStorage())
            app.router.add_endpoint('/', ['GET'], EndPoint(handler))
            request = create_http_request(app)
            request.cookies['_stormhttp_session'] = '{"a":1}'
            await app.router.route_request(request)

        asyncio.get_event_loop().run_until_complete(main())