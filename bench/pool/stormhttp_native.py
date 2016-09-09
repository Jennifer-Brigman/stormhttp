import asyncio
import time
import stormhttp
import sys
import math

URL = "http://www.example.com"
NUMBER_OF_REQUESTS = 10000
NUMBER_OF_SESSIONS = int(math.ceil(math.sqrt(NUMBER_OF_REQUESTS)))


def report(total_time: float):
    sys.stdout.write("{0:.5f} requests / second".format(NUMBER_OF_REQUESTS / total_time))
    sys.stdout.flush()


async def main():
    loop = asyncio.get_event_loop()
    pool = stormhttp.client.ClientSessionPool(NUMBER_OF_SESSIONS)
    url = URL.encode("utf-8")
    method = b'GET'
    futures = []
    range_iter = range(NUMBER_OF_REQUESTS)

    start_time = time.time()  # --- START TIMER ---
    for _ in range_iter:
        futures.append(loop.create_task(pool.request(url, method)))
    for future in futures:
        await future
    end_time = time.time()  # --- STOP TIMER ----

    report(end_time - start_time)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
