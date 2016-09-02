import asyncio
import stormhttp

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(stormhttp.server.Server().run("0.0.0.0", 8080))
    asyncio.get_event_loop().run_forever()