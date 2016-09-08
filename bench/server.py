import asyncio
import stormhttp

SIZE_OF_RESPONSE = 100 * 1024
RESPONSE_DATA = b'x' * SIZE_OF_RESPONSE


async def handler(_) -> stormhttp.HttpResponse:
    response = stormhttp.HttpResponse(status_code=200, status=b'OK')
    response.body = RESPONSE_DATA
    return response

if __name__ == "__main__":
    server = stormhttp.server.Server()
    server.router.add_route(b'/', b'GET', handler)
    server.run("localhost", 8080)
