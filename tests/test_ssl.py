import asyncio
import unittest
import stormhttp


class TestSSLCertificate(unittest.TestCase):
    def test_ssl_with_redirects(self):
        async def main():
            session = stormhttp.client.ClientSession()
            response = await session.request(b'https://google.com/', b'GET')
            self.assertTrue(True, "Didn't raise SSLError when redirecting")
            self.assertEqual(response.status_code, 200)
        asyncio.get_event_loop().run_until_complete(main())

    def test_ssl_cert_expired(self):
        async def main():
            session = stormhttp.client.ClientSession()
            with self.assertRaises(stormhttp.errors.SslCertificateError):
                await session.request(b'https://expired.badssl.com/', b'GET')
        asyncio.get_event_loop().run_until_complete(main())

    def test_ssl_cert_wrong_host(self):
        async def main():
            session = stormhttp.client.ClientSession()
            with self.assertRaises(stormhttp.errors.SslCertificateError):
                await session.request(b'https://wrong.host.badssl.com/', b'GET')
        asyncio.get_event_loop().run_until_complete(main())

    def test_ssl_cert_self_signed(self):
        async def main():
            session = stormhttp.client.ClientSession()
            with self.assertRaises(stormhttp.errors.SslCertificateError):
                await session.request(b'https://self-signed.badssl.com/', b'GET')
        asyncio.get_event_loop().run_until_complete(main())

    def test_ssl_cert_incomplete_chain(self):
        async def main():
            session = stormhttp.client.ClientSession()
            with self.assertRaises(stormhttp.errors.SslCertificateError):
                await session.request(b'https://incomplete-chain.badssl.com/', b'GET')
        asyncio.get_event_loop().run_until_complete(main())

    def test_ssl_cert_sha256(self):
        async def main():
            session = stormhttp.client.ClientSession()
            await session.request(b'https://sha256.badssl.com/', b'GET')
            self.assertTrue(True, "Didn't raise SSLError for SHA256.")
        asyncio.get_event_loop().run_until_complete(main())