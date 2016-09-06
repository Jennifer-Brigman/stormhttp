import asyncio
import time
import stormhttp

NUMBER_OF_REQUESTS = 1000
NUMBER_OF_SESSIONS = 10


async def main():
    pool = stormhttp.client.ClientSessionPool(NUMBER_OF_SESSIONS)
    url = b'http://www.example.com'
    method = b'GET'
    futures = []
    range_iter = range(NUMBER_OF_REQUESTS)

    print("Starting benchmark for {} requests with {} sessions in the pool.".format(NUMBER_OF_REQUESTS, NUMBER_OF_SESSIONS))

    start_time = time.time()  # --- START TIMER ---
    for _ in range_iter:
        futures.append(pool.request(url, method))
    for future in futures:
        await future
    end_time = time.time()    # --- STOP TIMER ----

    print("Achieved an average of {0:.4f}ms per request.".format((end_time - start_time) * 1000 / NUMBER_OF_REQUESTS))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
