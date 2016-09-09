import stormhttp
import time
import sys

RAW_RESPONSE = b'''HTTP/1.1 200 OK
Cache-Control: no-cache
Content-Encoding: gzip
Content-Type: text/html; charset=utf-8
Date: Tue, 06 Sep 2016 21:24:53 GMT
Server: GitHub.com
Set-Cookie: _octo=GH1.1.1218241880.1464796973; path=/; expires=Tue, 20 Sep 2016 21:24:53 -0000; secure; HttpOnly
Status: 200 OK
Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
Vary: X-PJAX, Accept-Encoding

'''
NUMBER_OF_TIMES_TO_BUILD = 100000


def report(total_time: float):
    sys.stdout.write("{0:.5f} responses / second".format(NUMBER_OF_TIMES_TO_BUILD / total_time))
    sys.stdout.flush()


if __name__ == "__main__":
    request = stormhttp.HttpResponse()
    parser = stormhttp.HttpParser(request)
    parser.feed_data(RAW_RESPONSE)
    total_time = 0

    for _ in range(NUMBER_OF_TIMES_TO_BUILD):
        start_time = time.time()  # --- START TIMER ---
        request.to_bytes()
        end_time = time.time()    # --- STOP TIMER ----
        total_time += (end_time - start_time)

    report(total_time)
