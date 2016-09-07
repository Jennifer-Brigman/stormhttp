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

Or if you want to work with the latest development version you may download from git.
```
git clone https://www.github.com/SethMichaelLarson/stormhttp.git
cd stormhttp && python setup.py install
```

## Features

- Complete HTTP client and server functionality.
- Super fast HTTP [parser](https://github.com/MagicStack/httptools/) and builder.
- Extremely flexible by having minimal decisions made for you. Power users rejoice!
- Support SSL/TLS for HTTPS connections.
- Cookies that can be stored offline for future Client sessions.
- Tons of optional extensions like sessions, CORS, authentication, all ready to use!

... and many more! [View our documentation](https://github.com/SethMichaelLarson/stormhttp/docs) for a complete list of features.

## Benchmarks

Did I mention that Stormhttp is lightning-fast?

#### Stormhttp

```
Running 30s test @ http://127.0.0.1:8080
  250 threads and 500 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    78.36ms   79.95ms   1.98s    98.99%
    Req/Sec    27.64     12.22   393.00     85.80%
  184852 requests in 30.10s, 17.64GB read
  Socket errors: connect 0, read 0, write 0, timeout 219
Requests/sec:   6141.12
Transfer/sec:    600.12MB
```

#### Aiohttp

```
Running 30s test @ http://127.0.0.1:8080
  250 threads and 500 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   163.17ms   88.69ms   1.99s    89.03%
    Req/Sec    12.92      7.72   240.00     91.12%
  64520 requests in 30.10s, 6.16GB read
  Socket errors: connect 0, read 0, write 0, timeout 340
Requests/sec:   2143.44
Transfer/sec:    209.57MB
```

#### Albatross

```
Running 30s test @ http://127.0.0.1:8000
  250 threads and 500 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    61.31ms   50.85ms   1.66s    98.87%
    Req/Sec    20.34      9.82    40.00     62.46%
  54645 requests in 30.10s, 5.21GB read
  Socket errors: connect 0, read 54703, write 0, timeout 36
Requests/sec:   1815.65
Transfer/sec:    177.43MB
```

## License

Stormhttp is licensed under the Apache 2.0 license.
