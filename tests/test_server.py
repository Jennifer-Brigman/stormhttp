import asyncio
import unittest


class FakeTransport(asyncio.WriteTransport):
    def write(self, data: bytes):
        pass


class TestServer(unittest.TestCase):
    def test_single_route(self):
        import stormhttp

        async def main():
            server = stormhttp.server.Server()

            def handler(_):
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                response.body = b'pass'
                return response

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/')
            request.method = b'GET'
            request.version = b'1.1'

            server.add_route(b'/', b'GET', handler)
            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertEqual(response.body, b'pass')

        asyncio.get_event_loop().run_until_complete(main())

    def test_long_route(self):
        import stormhttp

        async def main():
            server = stormhttp.server.Server()

            def handler(_):
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                response.body = b'pass'
                return response

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/a/b/c/d/e/f/g')
            request.method = b'GET'
            request.version = b'1.1'

            server.add_route(b'/a/b/c/d/e/f/g', b'GET', handler)
            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertEqual(response.body, b'pass')

        asyncio.get_event_loop().run_until_complete(main())

    def test_no_route_404(self):
        import stormhttp

        async def main():
            server = stormhttp.server.Server()

            def handler(_):
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                response.body = b'pass'
                return response

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/foo')
            request.method = b'GET'
            request.version = b'1.1'

            server.add_route(b'/bar', b'GET', handler)
            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())

    def test_no_method_403(self):
        import stormhttp

        async def main():
            server = stormhttp.server.Server()

            def handler(_):
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                response.body = b'pass'
                return response

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/foo')
            request.method = b'GET'
            request.version = b'1.1'

            server.add_route(b'/foo', b'POST', handler)
            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertEqual(response.status_code, 405)
            self.assertEqual(response.headers.get(b'Allow'), [b'POST'])

        asyncio.get_event_loop().run_until_complete(main())

    def test_all_encodings(self):
        import stormhttp
        import stormhttp.primitives.message

        async def main():
            server = stormhttp.server.Server()

            def handler(_):
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                response.body = b'x' * (1024 * 100)
                response.status_code = 200
                return response

            server.add_route(b'/', b'GET', handler)

            for encoding in stormhttp.primitives.message._SUPPORTED_ENCODINGS:
                if encoding == b'identity':
                    continue
                request = stormhttp.HttpRequest()
                request.url = stormhttp.HttpUrl(path=b'/')
                request.method = b'GET'
                request.version = b'1.1'
                request.headers[b'Accept-Encoding'] = encoding

                response = await server.route_request(request, FakeTransport(), get_response=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers.get(b'Content-Encoding'), [encoding])

        asyncio.get_event_loop().run_until_complete(main())

    def test_head_same_as_get_without_body(self):
        import stormhttp

        async def main():
            server = stormhttp.server.Server()

            def handler(_):
                response = stormhttp.HttpResponse(status=b'OK', status_code=200)
                response.body = b'pass'
                response.status_code = 200
                return response

            request = stormhttp.HttpRequest()
            request.url = stormhttp.HttpUrl(path=b'/foo')
            request.method = b'HEAD'
            request.version = b'1.1'

            server.add_route(b'/foo', b'GET', handler)
            response = await server.route_request(request, FakeTransport(), get_response=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.body, b'')

        asyncio.get_event_loop().run_until_complete(main())
