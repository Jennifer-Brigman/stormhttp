import abc
import asyncio
import math
import sys
import time
from multiprocessing import Pool

try:
    import uvloop
except ImportError:
    pass

import aiohttp
import stormhttp
import requests


class AbstractBenchmark(abc.ABC):
    def __init__(self, name: str, use_uvloop: bool=False):
        self.name = name
        self.use_uvloop = use_uvloop
        self.total_time = 0.0
        if self.use_uvloop:
            self.name += "_uvloop"

    async def start(self):
        sys.stdout.write("Running {} ... ".format(self.name))
        sys.stdout.flush()
        if asyncio.iscoroutinefunction(self.run):
            start_time = time.time()
            await self.run()
            end_time = time.time()
        else:
            start_time = time.time()
            self.run()
            end_time = time.time()
        self.total_time = end_time - start_time
        sys.stdout.write(self.report(end_time - start_time) + "\n")
        sys.stdout.flush()

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def report(self, seconds: float) -> str:
        pass


class GetBenchmark(AbstractBenchmark):
    def __init__(self, name: str, use_uvloop: bool=False):
        self.url = "http://www.example.com"
        self.number_of_requests = 100
        AbstractBenchmark.__init__(self, "get." + name, use_uvloop)

    def report(self, seconds: float):
        return "{0:.5f} requests / second".format(self.number_of_requests / seconds)


class PoolBenchmark(AbstractBenchmark):
    def __init__(self, name: str, async: bool=False):
        self.url = "http://www.example.com"
        self.number_of_requests = 500
        self.number_of_sessions = int(math.ceil(math.sqrt(self.number_of_requests)))
        AbstractBenchmark.__init__(self, "pool." + name, async)

    def report(self, seconds: float):
        return "{0:.5f} requests / second".format(self.number_of_requests / seconds)


class ParseRequestBenchmark(AbstractBenchmark):
    def __init__(self, name):
        self.raw_request = b'''GET /SethMichaelLarson/stormhttp HTTP/1.1
Host: github.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Cookie: _octo=GH1.1.1218241880.1464796973; logged_in=yes; _ga=GA1.2.460094502.1469803443; tz=America%2FChicago; _gat=1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0

'''
        self.number_of_requests = 100000
        AbstractBenchmark.__init__(self, "parse_request." + name)

    def report(self, seconds: float):
        return "{0:.5f} requests / second".format(self.number_of_requests / seconds)

# ----------------------
# Stormhttp
# ----------------------


class StormhttpGetBenchmark(GetBenchmark):
    def __init__(self, use_uvloop=False):
        GetBenchmark.__init__(self, "stormhttp", use_uvloop)

    async def run(self):
        session = stormhttp.client.ClientSession()
        url = self.url.encode("utf-8")
        for _ in range(self.number_of_requests):
            await session.request(url, b'GET')


class StormhttpPoolBenchmark(PoolBenchmark):
    def __init__(self, use_uvloop=False):
        PoolBenchmark.__init__(self, "stormhttp", use_uvloop)

    async def run(self):
        loop = asyncio.get_event_loop()
        pool = stormhttp.client.ClientSessionPool(self.number_of_sessions)
        url = self.url.encode("utf-8")
        futures = []

        for _ in range(self.number_of_requests):
            futures.append(loop.create_task(pool.request(url, b'GET')))
        for future in futures:
            await future


class StormhttpParseRequestBenchmark(ParseRequestBenchmark):
    def __init__(self):
        ParseRequestBenchmark.__init__(self, "stormhttp")

    def run(self):
        parser = stormhttp.HttpParser()
        for _ in range(self.number_of_requests):
            parser.set_target(stormhttp.HttpRequest())
            parser.feed_data(self.raw_request)


# ----------------------
# Aiohttp
# ----------------------


class AiohttpGetBenchmark(GetBenchmark):
    def __init__(self, use_uvloop=False):
        GetBenchmark.__init__(self, "aiohttp", use_uvloop)

    async def run(self):
        async with aiohttp.ClientSession() as session:
            for _ in range(self.number_of_requests):
                async with session.get(self.url) as resp:
                    resp.text()


# ----------------------
# Requests
# ----------------------


class RequestsPoolBenchmark(PoolBenchmark):
    def __init__(self):
        PoolBenchmark.__init__(self, "requests")

    def run(self):
        urls = [self.url] * self.number_of_requests
        with Pool(self.number_of_sessions) as p:
            p.map(requests.get, urls)


class RequestsGetBenchmark(GetBenchmark):
    def __init__(self):
        GetBenchmark.__init__(self, "requests")

    def run(self):
        for _ in range(self.number_of_requests):
            requests.get(self.url)


if __name__ == "__main__":
    benchmarks_to_run = {
        "get": [
            StormhttpGetBenchmark(),
            RequestsGetBenchmark(),
            AiohttpGetBenchmark()
        ],
        "pool": [
            StormhttpPoolBenchmark(),
            RequestsPoolBenchmark()
        ],
        "parse_request": [
            StormhttpParseRequestBenchmark()
        ]
    }

    try:
        import uvloop
        benchmarks_to_run["get"].extend([
            StormhttpGetBenchmark(True),
            AiohttpGetBenchmark(True),
        ])
        benchmarks_to_run["pool"].extend([
            StormhttpPoolBenchmark(True),
        ])
    except ImportError:
        pass

    for benchmark_group in benchmarks_to_run:

        print("---- Running benchmark: {} ----\n".format(benchmark_group))

        for benchmark_in_group in benchmarks_to_run[benchmark_group]:
            if benchmark_in_group.use_uvloop:
                asyncio.set_event_loop(uvloop.new_event_loop())
            else:
                asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.get_event_loop().run_until_complete(benchmark_in_group.start())
        benchmark_sorted = sorted(benchmarks_to_run[benchmark_group], key=lambda k: k.total_time)
        benchmark_winner = benchmark_sorted[0]

        print("\n---- Results ----\n")

        for benchmark_in_group in benchmark_sorted[1:]:
            print("{0} is {1:.3f}% faster than {2}".format(benchmark_winner.name, benchmark_in_group.total_time / benchmark_winner.total_time * 100.0, benchmark_in_group.name))

        print("")

