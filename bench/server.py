import asyncio
import stormhttp

SIZE_OF_RESPONSE = 1024 * 100  # 100 Kibibytes
RESPONSE_DATA = b'x' * SIZE_OF_RESPONSE


async def handler(request: stormhttp.HttpRequest) -> stormhttp.HttpResponse:
    response = stormhttp.HttpResponse()
    response.status_code = 200
    response.status = b'OK'
    response.body = RESPONSE_DATA
    response.headers[b'Content-Length'] = SIZE_OF_RESPONSE
    return response

async def main():
    server = stormhttp.server.Server()
    server.router.add_route(b'/', b'GET', handler)
    await server.run("localhost", 8080)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
