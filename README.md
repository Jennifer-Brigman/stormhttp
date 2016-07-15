# Stormsurge
Performant asynchronous web application framework built on [httptools](https://github.com/MagicStack/httptools) for Python 3.5+

[![Travis](https://img.shields.io/travis/SethMichaelLarson/Stormsurge.svg?maxAge=2592000)]()
[![Requires.io](https://img.shields.io/requires/github/SethMichaelLarson/Stormsurge.svg?maxAge=2592000)]()
[![Coveralls](https://img.shields.io/coveralls/SethMichaelLarson/Stormsurge.svg?maxAge=2592000)]()

Version `0.0.1 alpha`


### Benchmarks
Benchmarks both use `wrk -t250 -c500 -d30 http://127.0.0.1:5000` to create connections.

#### Stormsurge
```
Running 30s test @ http://127.0.0.1:5000
  250 threads and 500 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    40.41ms   66.30ms   1.64s    98.66%
    Req/Sec    33.36     14.32   330.00     73.59%
  114018 requests in 30.10s, 10.88GB read
  Socket errors: connect 0, read 0, write 0, timeout 63
Requests/sec:   3787.85
Transfer/sec:    370.13MB
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
