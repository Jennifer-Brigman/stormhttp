import asyncio
import unittest
try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


def create_standard_request(url=b'/'):
    from stormhttp.web import HTTPRequest
    import httptools
    request = HTTPRequest()
    request.url = httptools.parse_url(url)
    request.method = b'GET'
    return request


class TestHTTPRouter(unittest.TestCase):
    def test_add_simple_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/', {b'GET'}, ConstantEndPoint(b'test'))
            request = create_standard_request()

            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_multiple_methods(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/', {b'GET', b'POST'}, ConstantEndPoint(b'test'))
            request = create_standard_request()

            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')
            self.assertEqual(response.status_code, 200)

            request = create_standard_request()
            request.method = b'POST'
            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_duplicate_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/', {b'GET'}, ConstantEndPoint(b'test'))
            with self.assertRaises(ValueError):
                router.add_endpoint(b'/', {b'GET'}, ConstantEndPoint(b'test'))

        asyncio.get_event_loop().run_until_complete(main())

    def test_match_info_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/{a}', {b'GET'}, ConstantEndPoint(b'test'))

            request = create_standard_request(b'/1')
            await router.route_request(request)
            self.assertIn(b'a', request.match_info)
            self.assertEqual(request.match_info[b'a'], b'1')

        asyncio.get_event_loop().run_until_complete(main())

    def test_match_info_duplicate_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/{a}', {b'GET'}, ConstantEndPoint(b'test'))
            with self.assertRaises(ValueError):
                router.add_endpoint(b'/{a}', {b'GET'}, ConstantEndPoint(b'test'))

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_long_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a/b/c/d/e', [b'GET'], ConstantEndPoint(b'test'))

            request = create_standard_request(b'/a/b/c/d/e')
            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_trailing_slash_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a/b/c/d/e/', [b'GET'], ConstantEndPoint(b'test'))

            request = create_standard_request(b'/a/b/c/d/e')
            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_found_route_existing_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a', [b'GET'], ConstantEndPoint(b'test'))

            request = create_standard_request(b'/b')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_found_route_no_routes(self):
        async def main():
            from stormhttp.router import Router

            loop = asyncio.get_event_loop()
            router = Router(loop)

            request = create_standard_request(b'/')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_allowed_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a', [b'POST', b'HEAD'], ConstantEndPoint(b'test'))

            request = create_standard_request(b'/a')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 405)
            self.assertIn(response.headers[b'Allow'], [b'POST,HEAD', b'HEAD,POST'])

        asyncio.get_event_loop().run_until_complete(main())

    def test_partial_route(self):
        async def main():
            from stormhttp.router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a/b/c', [b'GET'], ConstantEndPoint(b'test'))

            request = create_standard_request(b'/a/b')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())