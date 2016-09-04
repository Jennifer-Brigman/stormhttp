# Stormhttp
Lightning-fast asynchronous web framework for Python 3.5+. Built to be a speedy lower-level replacement for aiohttp.
Stormhttp is encoding-agnostic as all work is done on raw bytes rather than strings.
We leave all those issues up to the application which allows both greater control and speed.

[![Travis Master](https://img.shields.io/travis/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://travis-ci.org/SethMichaelLarson/stormhttp/branches)
[![Coveralls Master](https://img.shields.io/coveralls/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://coveralls.io/github/SethMichaelLarson/stormhttp)
[![Requires.io](https://img.shields.io/requires/github/SethMichaelLarson/stormhttp.svg?maxAge=300)](https://requires.io/github/SethMichaelLarson/stormhttp/requirements)
[![PyPI](https://img.shields.io/pypi/v/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)
[![PyPI](https://img.shields.io/pypi/dm/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)

### Example Usage

```python
import datetime
import stormhttp

# Parsing a request
req = stormhttp.primitives.HttpRequest()
par = stormhttp.primitives.HttpParser(req)
par.feed_data(b'''GET /login HTTP/1.1
Host: www.example.com
Cookie: a=1; b=2;

''')

# Accessing the parsed values
print(req.method)           # b'GET'
print(req.version)          # b'1.1'
print(req.headers[b'Host']) # [b'www.example.com']
print(req.cookies[b'a'])    # b'1'
print(req.url.path)         # b'/login'

# Crafting a response
res = stormhttp.primitives.HttpResponse()
res.version = b'2.0'
res.status = 'OK'
res.status_code = 200
res.headers[b'Content-Type'] = b'text/html'
res.cookies[b'foo'] = b'bar'
res.cookies.set_meta(b'foo', http_only=True, expires=datetime.datetime.utcnow())
res.body = b'Hello, world!'

# Sending the bytes over the wire
print(res.to_bytes().decode("utf-8"))

# HTTP/2.0 200 OK
# CONTENT-TYPE: text/html
# SET-COOKIE: foo=bar; HttpOnly; Expires=Fri, 26 Aug 2016 20:13:10 GMT;
#
# Hello, world!
```
