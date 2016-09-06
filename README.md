[![Travis Master](https://img.shields.io/travis/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://travis-ci.org/SethMichaelLarson/stormhttp/branches)
[![Coveralls Master](https://img.shields.io/coveralls/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://coveralls.io/github/SethMichaelLarson/stormhttp)
[![Requires.io](https://img.shields.io/requires/github/SethMichaelLarson/stormhttp.svg?maxAge=300)](https://requires.io/github/SethMichaelLarson/stormhttp/requirements)
[![PyPI](https://img.shields.io/pypi/v/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)
[![PyPI](https://img.shields.io/pypi/dm/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)

Lightning-fast asynchronous web framework for Python 3.5+. Suitable for both client and server use-cases. Built to be a speedy lower-level replacement for aiohttp without sacrificing usability.

> **NOTE:** This project is currently in alpha (>0.1.0) and therefore may not be suitable for production environments.

## Installation

Stormhttp requires Python 3.5 and is [available on PyPI](https://pypi.python.org/pypi/stormhttp). Use pip to install it ([Using a virtual environment is encouraged](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwj90s7yr_vOAhUYzmMKHUBfDBMQFggeMAA&url=http%3A%2F%2Fdocs.python-guide.org%2Fen%2Flatest%2Fdev%2Fvirtualenvs%2F&usg=AFQjCNEvupNSRAVxfumkI5JFoxABd0GHhQ)):

```
python -m pip install stormhttp
```

## Features
:tada: Complete HTTP client and server functionality.

:rocket: Super fast HTTP [parser](https://github.com/MagicStack/httptools/) and builder.

:envelope: Easy-to-use containers for HTTP messages.

:lock: Support SSL/TLS for HTTPS connections.

:cookie: Cookies that can be stored offline for future Client sessions.

:alien: Cross-Origin Resource Sharing management.

:zzz: Completely asynchronous, no more blocking!

... and many more! [View our documentation](https://github.com/SethMichaelLarson/stormhttp/docs) for a complete list of features.

## Using Stormhttp

```python
import datetime
import stormhttp

# Parsing a request
req = stormhttp.HttpRequest()
par = stormhttp.HttpParser(req)
par.feed_data(b'''GET /login HTTP/1.1
Accept: text/html,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip, deflate, br
Host: www.example.com
Cookie: a=1; b=2;

''')

# Accessing the parsed values
print(req.method)           # b'GET'
print(req.version)          # b'1.1'
print(req.headers[b'Host']) # [b'www.example.com']
print(req.cookies.all())    # {b'a': b'1', b'b': b'2'}
print(req.url.path)         # b'/login'

# HttpHeaders can parse q-values for you!
print(req.headers.qlist(b'Accept')) # [(b'text/html', 1.0), (b'application/xml', 0.9), (b'*/*', 0.8)]

# Also works for lists with no q-values. Preserves order!
print(req.headers.qlist(b'Accept-Encoding')) # [(b'gzip', 1.0), (b'deflate', 1.0), (b'br', 1.0)]

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

## License

Stormhttp is licensed under the Apache 2.0 license.
