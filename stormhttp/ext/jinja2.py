import asyncio
import jinja2
import types
import typing
import stormhttp


__all__ = [
    "setup",
    "Jinja2EndPoint"
]
_APP_KEY = "stormhttp_jinja2_env"


def setup(app: stormhttp.web.Application, *args, **kwargs) -> jinja2.Environment:
    """
    Applies the Jinja2 environment to the Application.
    :param app: Application to bind to.
    :param args: Arguments to pass to the jinja2.Environment.
    :param kwargs: Kwargs to pass to the jinja2.Environment.
    :return: The created jinja2.Environment.
    """
    env = jinja2.Environment(*args, **kwargs)
    app[_APP_KEY] = env
    env.globals["app"] = app
    return env


class Jinja2EndPoint(stormhttp.web.AbstractEndPoint):
    def __init__(self, template_name: str, handler: typing.Callable[[stormhttp.web.HTTPRequest],
                typing.Union[typing.Mapping, types.CoroutineType]], encoding="utf-8"):
        self._template_name = template_name
        self._handler = handler
        self._encoding = encoding

    async def on_request(self, loop: asyncio.AbstractEventLoop, request: stormhttp.web.HTTPRequest):
        if asyncio.iscoroutinefunction(self._handler):
            context = await self._handler(request)
        else:
            context = self._handler(request)
        env = request.app.get(_APP_KEY, None)
        if env is None:
            response = stormhttp.web.HTTPErrorResponse(500)
            response.body = 'Template engine is not initialized. Call stormhttp_jinja2.setup(...) first.'
            return response
        try:
            template = env.get_template(self._template_name)
        except jinja2.TemplateNotFound:
            response = stormhttp.web.HTTPErrorResponse(500)
            response.body = 'Template \'%s\' not found.' % (self._template_name.encode("utf-8"),)
            return response
        if not isinstance(context, typing.Mapping):
            response = stormhttp.web.HTTPErrorResponse(500)
            response.body = 'Context should be of type mapping, not \'%s\'.' % (str(type(context)),)
            return response
        response = stormhttp.web.HTTPResponse()
        response.body = template.render(context)
        response.headers['Content-Type'] = 'text/html; charset=%s' % (self._encoding,)
        return response
