# stormhttp
Performant asynchronous web application framework built on [httptools](https://github.com/MagicStack/httptools) for Python 3.5+

Version `0.0.3 Alpha`

[![Travis Master](https://img.shields.io/travis/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://travis-ci.org/SethMichaelLarson/stormhttp/branches)
[![Coveralls Master](https://img.shields.io/coveralls/SethMichaelLarson/stormhttp/master.svg?maxAge=300)](https://coveralls.io/github/SethMichaelLarson/stormhttp?branch=master)
[![Requires.io](https://img.shields.io/requires/github/SethMichaelLarson/stormhttp.svg?maxAge=300)](https://requires.io/github/SethMichaelLarson/stormhttp/requirements/?branch=develop)

### Benchmarks
Benchmarks both use `wrk -t250 -c500 -d30 http://127.0.0.1:5000` to create connections.

#### stormhttp
```
Running 30s test @ http://127.0.0.1:5000
  250 threads and 500 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    38.70ms   59.16ms   1.79s    98.92%
    Req/Sec    33.58     13.62   100.00     76.17%
  115776 requests in 30.10s, 11.05GB read
  Socket errors: connect 0, read 0, write 0, timeout 40
Requests/sec:   3846.43
Transfer/sec:    375.86MB
```

#### aiohttp
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
