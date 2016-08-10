import asyncio
import httptools
import unittest
from stormhttp.web import Application, HTTPRequest, HTTPResponse, Endpoint
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
            stormhttp.ext.session.setup(app, stormhttp.ext.session.SimpleCookieStorage())
            app.router.add_endpoint('/', ['GET'], Endpoint(handler))
            await app.router.route_request(create_http_request(app))

        asyncio.get_event_loop().run_until_complete(main())

    def test_save_simple_session(self):
        async def main():
            async def handler(request: HTTPRequest):
                self.assertTrue(hasattr(request, "session"))
                return request.decorate_response(HTTPResponse())

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.session.setup(app, stormhttp.ext.session.SimpleCookieStorage())
            app.router.add_endpoint('/', ['GET'], Endpoint(handler))
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
            stormhttp.ext.session.setup(app, stormhttp.ext.session.SimpleCookieStorage())
            app.router.add_endpoint('/', ['GET'], Endpoint(handler))
            request = create_http_request(app)
            request.cookies['_stormhttp_session'] = '{"a":1}'
            await app.router.route_request(request)

        asyncio.get_event_loop().run_until_complete(main())

    def test_fernet_encrypt_session(self):
        async def main():
            async def handler(request: HTTPRequest):
                request.session["a"] = "1"
                return request.decorate_response(HTTPResponse())

            secret_key = b'a' * 32
            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.session.setup(app, stormhttp.ext.session.EncryptedCookieStorage(secret_key))
            app.router.add_endpoint('/', ['GET'], Endpoint(handler))
            request = create_http_request(app)
            response = await app.router.route_request(request)
            self.assertNotEqual(response.cookies["_stormhttp_session"], '{"a":1}')

        asyncio.get_event_loop().run_until_complete(main())

    def test_fernet_decrypt_session(self):
        async def main():
            async def handler(request: HTTPRequest):
                self.assertEqual(request.session["a"], "1")
                return request.decorate_response(HTTPResponse())

            secret_key = b'a' * 32
            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.session.setup(app, stormhttp.ext.session.EncryptedCookieStorage(secret_key))
            app.router.add_endpoint('/', ['GET'], Endpoint(handler))
            request = create_http_request(app)
            request.cookies["_stormhttp_session"] = "gAAAAABXm4KyrYOXQOcfRY-S1Q34KN2PXqjDyOjxSv38pJ_rU8M7an4K13YNahHSp7QpNbdL9Z-v0o_qhz_jkQ0SinWvVz13QQ=="
            await app.router.route_request(request)

        asyncio.get_event_loop().run_until_complete(main())