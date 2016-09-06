import asyncio
import unittest


class TestClientPool(unittest.TestCase):
    def test_client_pool_single_request(self):
        async def main():
            from stormhttp.client import ClientSessionPool
            pool = ClientSessionPool(1)
            response = await pool.request(b'http://www.example.com', b'GET')
            self.assertTrue(response.is_complete())

        asyncio.get_event_loop().run_until_complete(main())

    def test_client_pool_multiple_requests(self):
        async def main():
            from stormhttp.client import ClientSessionPool
            pool = ClientSessionPool(2)
            response1 = await pool.request(b'http://www.example.com', b'GET')
            response2 = await pool.request(b'http://www.example.com', b'GET')
            self.assertEqual(response1.body, response2.body)

        asyncio.get_event_loop().run_until_complete(main())

    def test_client_pool_concurrent_requests(self):
        async def main():
            from stormhttp.client import ClientSessionPool
            import time
            pool = ClientSessionPool(5)
            t = time.time()
            await pool.request(b'http://www.example.com', b'GET')
            single_rtt = time.time() - t

            futures = []
            t = time.time()
            for _ in range(10):
                futures.append(pool.request(b'http://www.example.com', b'GET'))
            for future in futures:
                await future
            ten_rtt = time.time() - t
            self.assertTrue(ten_rtt < single_rtt * 10)

        asyncio.get_event_loop().run_until_complete(main())
