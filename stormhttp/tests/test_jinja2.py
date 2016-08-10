import asyncio
import os
import unittest

import httptools
import jinja2

import stormhttp
import stormhttp.ext
import stormhttp.ext.jinja2
from stormhttp.web import Application, HTTPRequest

try:
    import uvloop
    asyncio.set_event_loop(uvloop.new_event_loop())
except ImportError:
    pass


_TEMPLATE_LOADER = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))


def create_http_request(app) -> HTTPRequest:
    request = HTTPRequest()
    request.url = httptools.parse_url(b'/')
    request.method = 'GET'
    request.version = '1.1'
    request.app = app
    return request


class TestJinja2Templating(unittest.TestCase):
    def test_simple_template(self):
        async def main():
            async def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.jinja2.setup(app, loader=_TEMPLATE_LOADER)
            app.router.add_endpoint('/', ['GET'], stormhttp.ext.jinja2.Jinja2Endpoint("jinja2.tmpl", handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.body, 'a = 0')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_coroutine_template(self):
        async def main():
            def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.jinja2.setup(app, loader=_TEMPLATE_LOADER)
            app.router.add_endpoint('/', ['GET'], stormhttp.ext.jinja2.Jinja2Endpoint("jinja2.tmpl", handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.body, 'a = 0')
            self.assertEqual(response.status_code, 200)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_found_template(self):
        async def main():
            async def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.jinja2.setup(app, loader=_TEMPLATE_LOADER)
            app.router.add_endpoint('/', ['GET'], stormhttp.ext.jinja2.Jinja2Endpoint("NOTFOUND.tmpl", handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.status_code, 500)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_initialized_template(self):
        async def main():
            async def handler(request: HTTPRequest):
                return {"a": 0}

            loop = asyncio.get_event_loop()
            app = Application(loop)
            app.router.add_endpoint('/', ['GET'], stormhttp.ext.jinja2.Jinja2Endpoint("jinja2.tmpl", handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.status_code, 500)

        asyncio.get_event_loop().run_until_complete(main())

    def test_not_mapping_template(self):
        async def main():
            async def handler(request: HTTPRequest):
                return 1

            loop = asyncio.get_event_loop()
            app = Application(loop)
            stormhttp.ext.jinja2.setup(app, loader=_TEMPLATE_LOADER)
            app.router.add_endpoint('/', ['GET'], stormhttp.ext.jinja2.Jinja2Endpoint("jinja2.tmpl", handler))
            response = await app.router.route_request(create_http_request(app))
            self.assertEqual(response.status_code, 500)

        asyncio.get_event_loop().run_until_complete(main())