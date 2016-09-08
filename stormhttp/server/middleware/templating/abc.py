import abc
import typing
from .. import AbstractMiddleware
from ....primitives import HttpRequest, HttpResponse, TemplateHttpResponse

__all__ = [
    "AbstractTemplatingMiddleware"
]


class AbstractTemplatingMiddleware(AbstractMiddleware):
    def __init__(self):
        self.route_templates = {}  # type: typing.Dict[bytes, str]
        AbstractMiddleware.__init__(self)

    def add_route(self, route: bytes, template_name: str):
        self.routes.add(route)
        self.route_templates[route] = template_name
        route = route.rstrip(b'/')
        if len(route):
            self.routes.add(route)
            self.route_templates[route] = template_name

    @abc.abstractmethod
    def render_template(self, route: bytes, environment: dict) -> bytes:
        pass

    def before_handler(self, request: HttpRequest):
        pass

    def after_handler(self, request: HttpRequest, response: HttpResponse):
        if not isinstance(response, TemplateHttpResponse):
            raise ValueError("Handler functions with a AbstractTemplatingMiddleware must return TemplateHttpResponse objects.")
        try:
            response.body = self.render_template(request.url.path, response.template_info)
        except Exception as error:
            response.body = str(error).encode("utf-8")
            response.status_code = 500
            response.status = b'Internal Server Error'
