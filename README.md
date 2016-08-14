# stormhttp
Lightning-quick HTTP primitives built on [httptools](https://github.com/MagicStack/httptools) for Python 3.5+

[![Travis Master](https://img.shields.io/travis/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://travis-ci.org/SethMichaelLarson/stormhttp/branches)
[![Coveralls Master](https://img.shields.io/coveralls/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://coveralls.io/github/SethMichaelLarson/stormhttp)
[![Requires.io](https://img.shields.io/requires/github/SethMichaelLarson/stormhttp.svg?maxAge=300)](https://requires.io/github/SethMichaelLarson/stormhttp/requirements)
[![PyPI](https://img.shields.io/pypi/v/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)
[![PyPI](https://img.shields.io/pypi/dm/stormhttp.svg?maxAge=300)](https://pypi.python.org/pypi/stormhttp)

### Example Usage

```python
import datetime
import stormhttp

# Crafting a response
r = stormhttp.HttpResponse()
r.version = b'2.0'
r.status = 'OK'
r.status_code = 200
r.headers[b'Content-Type'] = b'text/html'
r.cookies[b'a'] = b'1'
r.cookies.meta(b'a', http_only=True, expires=datetime.datetime.utcnow())
r.body = b'Hello, world!'
print(r.to_bytes().encode("utf-8"))

# HTTP/2.0 200 OK
# CONTENT-TYPE: text/html
# SET-COOKIE: foo=bar; HttpOnly; Expires=2016-08-14T21:01:34;
#
# Hello, world!
```