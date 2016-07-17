import asyncio
import unittest
try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


def create_standard_request(url=b'/'):
    from stormsurge._http import HTTPRequest
    import httptools
    request = HTTPRequest()
    request.url = httptools.parse_url(url)
    request.method = b'GET'
    return request


class TestHTTPRouter(unittest.TestCase):
    def test_add_simple_route(self):
        async def main():
            from stormsurge.router import Router
            from stormsurge._endpoints import SimpleEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/', {b'GET'}, SimpleEndPoint(b'test'))
            request = create_standard_request()

            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_multiple_methods(self):
        async def main():
            from stormsurge.router import Router
            from stormsurge._endpoints import SimpleEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/', {b'GET', b'POST'}, SimpleEndPoint(b'test'))
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
            from stormsurge.router import Router
            from stormsurge._endpoints import SimpleEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/', {b'GET'}, SimpleEndPoint(b'test'))
            with self.assertRaises(ValueError):
                router.add_endpoint(b'/', {b'GET'}, SimpleEndPoint(b'test'))

        asyncio.get_event_loop().run_until_complete(main())

    def test_match_info_route(self):
        async def main():
            from stormsurge.router import Router
            from stormsurge._endpoints import SimpleEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/{a}', {b'GET'}, SimpleEndPoint(b'test'))

            request = create_standard_request(b'/1')
            await router.route_request(request)
            self.assertIn(b'a', request.match_info)
            self.assertEqual(request.match_info[b'a'], b'1')

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_long_route(self):
        async def main():
            from stormsurge.router import Router
            from stormsurge._endpoints import SimpleEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a/b/c/d/e', [b'GET'], SimpleEndPoint(b'test'))

            request = create_standard_request(b'/a/b/c/d/e')
            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')

        asyncio.get_event_loop().run_until_complete(main())

    def test_add_trailing_slash_route(self):
        async def main():
            from stormsurge.router import Router
            from stormsurge._endpoints import SimpleEndPoint

            loop = asyncio.get_event_loop()
            router = Router(loop)
            router.add_endpoint(b'/a/b/c/d/e/', [b'GET'], SimpleEndPoint(b'test'))

            request = create_standard_request(b'/a/b/c/d/e')
            response = await router.route_request(request)
            self.assertEqual(response.body, b'test')

        asyncio.get_event_loop().run_until_complete(main())