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
req = stormhttp.HttpRequest()
par = stormhttp.HttpParser(req)
par.feed_data(b'''GET /login HTTP/1.1
Host: www.example.com
Cookie: a=1; b=2;

''')

# Accessing the parsed values
print(req.method)           # b'GET'
print(req.version)          # b'1.1'
print(req.headers[b'Host']) # [b'www.example.com']
print(req.cookies.all())    # {b'a': b'1', b'b': b'2'}
print(req.url.path)         # b'/login'

# Crafting a response
res = stormhttp.HttpResponse()
res.version = b'2.0'
res.status = 'OK'
res.status_code = 200
res.body = b'Hello, world!'
res.headers[b'Content-Type'] = b'text/html; charset=utf-8'
res.headers[b'Content-Length'] = len(res.body)  # It's fine to use integers! They're converted to bytes.

# Support for Cookies!
cookie = stormhttp.HttpCookie()
cookie.values[b'foo'] = b'bar'
cookie.http_only = True
cookie.expires = datetime.datetime.utcnow()
cookie.domain = b'.example.com'
cookie.path = b'/'
res.cookies.add(cookie)

# Sending the bytes over the wire
print(res.to_bytes().decode("utf-8"))

# HTTP/2.0 200 OK
# CONTENT-TYPE: text/html; charset=utf-8
# CONTENT-LENGTH: 13
# SET-COOKIE: foo=bar; Domain=.example.com; Path=/; Expires=Fri, 26 Aug 2016 20:13:10 GMT; HttpOnly;
#
# Hello, world!
```
