import asyncio
import unittest


class FakeTransport(asyncio.WriteTransport):
    def write(self, data: bytes):
        pass


class TestServerSessions(unittest.TestCase):
    def test_simple_session(self):
        import stormhttp

        async def main():

            def handler(request: stormhttp.HttpRequest):
                self.assertTrue(request.session is not None)
                request.session['foo'] = 'bar'
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                return response

            server = stormhttp.server.Server()
            server.add_route(b'/', b'GET', handler)

            session_middleware = stormhttp.server.middleware.SessionMiddleware(stormhttp.server.middleware.SimpleSessionStorage())
            session_middleware.add_route(b'/')
            server.add_middleware(session_middleware)

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/')
            request.method = b'GET'
            request.version = b'1.1'

            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertEqual(response.cookies.all().get(b'stormhttp_session'), b'{"foo": "bar"}')

        asyncio.get_event_loop().run_until_complete(main())

    def test_encrypted_session(self):
        import stormhttp

        async def main():
            def handler(request: stormhttp.HttpRequest):
                self.assertTrue(request.session is not None)
                request.session['foo'] = 'bar'
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                return response

            server = stormhttp.server.Server()
            server.add_route(b'/', b'GET', handler)

            session_middleware = stormhttp.server.middleware.SessionMiddleware(
                stormhttp.server.middleware.EncryptedSessionStorage(b'12345678901234567890123456789012'))
            session_middleware.add_route(b'/')
            server.add_middleware(session_middleware)

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/')
            request.method = b'GET'
            request.version = b'1.1'

            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertIn(b'stormhttp_session', response.cookies.all())
            self.assertNotIn(b'foo', response.cookies.all()[b'stormhttp_session'])
            self.assertNotIn(b'bar', response.cookies.all()[b'stormhttp_session'])

        asyncio.get_event_loop().run_until_complete(main())
