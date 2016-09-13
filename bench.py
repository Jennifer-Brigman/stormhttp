import stormhttp
import uvloop

response = stormhttp.HttpResponse()
response.body = b'x' * (1024 * 100)
response.version = b'1.1'
response.status = b'OK'
response.status_code = 200
response.headers[b'Content-Length'] = (1024 * 100)


def handler(_):
    return response

if __name__ == "__main__":
    server = stormhttp.server.Server(loop=uvloop.new_event_loop())
    server.add_route(b'/', b'GET', handler)
    server.run("0.0.0.0", 8080)
