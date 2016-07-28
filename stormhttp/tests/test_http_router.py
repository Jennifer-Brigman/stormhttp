import asyncio
import unittest
try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


def create_standard_request(url: bytes=b"/"):
    from stormhttp.web import HTTPRequest
    import httptools
    request = HTTPRequest()
    request.url = httptools.parse_url(url)
    request.method = 'GET'
    request.version = '1.1'
    return request


class TestHTTPRouter(unittest.TestCase):
    def test_add_simple_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint("/", ["GET"], ConstantEndPoint('test'))
            request = create_standard_request()

            response = await router.route_request(request)
            self.assertEqual(response.body, 'test')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_multiple_methods(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint("/", {'GET', 'POST'}, ConstantEndPoint('test'))
            request = create_standard_request()

            response = await router.route_request(request)
            self.assertEqual(response.body, 'test')
            self.assertEqual(response.status_code, 200)

            request = create_standard_request()
            request.method = 'POST'
            response = await router.route_request(request)
            self.assertEqual(response.body, 'test')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_duplicate_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint("/", ["GET"], ConstantEndPoint('test'))
            with self.assertRaises(ValueError):
                router.add_endpoint("/", ["GET"], ConstantEndPoint('test'))

        asyncio.get_event_loop().run_until_complete(main())

    def test_match_info_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/{a}', ["GET"], ConstantEndPoint('test'))

            request = create_standard_request(b'/1')
            await router.route_request(request)
            self.assertIn('a', request.match_info)
            self.assertEqual(request.match_info['a'], '1')

        asyncio.get_event_loop().run_until_complete(main())

    def test_match_info_duplicate_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/{a}', ["GET"], ConstantEndPoint('test'))
            with self.assertRaises(ValueError):
                router.add_endpoint('/{a}', ["GET"], ConstantEndPoint('test'))

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_long_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/a/b/c/d/e', ['GET'], ConstantEndPoint('test'))

            request = create_standard_request(b'/a/b/c/d/e')
            response = await router.route_request(request)
            self.assertEqual(response.body, 'test')

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_trailing_slash_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/a/b/c/d/e/', ['GET'], ConstantEndPoint('test'))

            request = create_standard_request(b'/a/b/c/d/e')
            response = await router.route_request(request)
            self.assertEqual(response.body, 'test')

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_found_route_existing_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/a', ['GET'], ConstantEndPoint('test'))

            request = create_standard_request(b'/b')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_found_route_no_routes(self):
        async def main():
            from stormhttp._router import Router

            loop = asyncio.get_event_loop()
            router = Router(loop)

            request = create_standard_request()
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_allowed_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/a', ['POST', 'HEAD'], ConstantEndPoint('test'))

            request = create_standard_request(b'/a')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 405)
            self.assertIn(response.headers['Allow'], ['POST,HEAD', 'HEAD,POST'])

        asyncio.get_event_loop().run_until_complete(main())

    def test_partial_route(self):
        async def main():
            from stormhttp._router import Router
            from stormhttp._endpoints import ConstantEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint('/a/b/c', ['GET'], ConstantEndPoint('test'))

            request = create_standard_request(b'/a/b')
            response = await router.route_request(request)
            self.assertEqual(response.status_code, 404)

        asyncio.get_event_loop().run_until_complete(main())