import asyncio
import stormhttp
import time

async def main():
    client = stormhttp.client.ClientSessionPool(100)
    futs = []
    loop = asyncio.get_event_loop()
    await client.request(b'http://www.google.com', b'GET')
    t = time.time()
    for _ in range(1000):
        futs.append(loop.create_task(client.request(b'http://www.google.com', b'GET')))
    for f in futs:
        await f
    print((time.time() - t) / 1000)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
