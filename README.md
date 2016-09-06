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

### License

Stormhttp is licensed under the Apache 2.0 license.

Copyright 2016 Seth Michael Larson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
