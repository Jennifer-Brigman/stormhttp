import jinja2
from .abc import AbstractTemplatingMiddleware

__all__ = [
    "Jinja2TemplatingMiddleware"
]


class Jinja2TemplatingMiddleware(AbstractTemplatingMiddleware):
    def __init__(self, environment: jinja2.Environment):
        self.environment = environment
        AbstractTemplatingMiddleware.__init__(self)

    def render_template(self, route: bytes, environment: dict) -> bytes:
        return self.environment.get_template(self.route_templates[route]).render(**environment).encode(self.encoding)
