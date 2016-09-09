import stormhttp
import time
import sys

RAW_REQUEST = b'''GET /SethMichaelLarson/stormhttp HTTP/1.1
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
NUMBER_OF_TIMES_TO_BUILD = 100000


def report(total_time: float):
    sys.stdout.write("{0:.5f} requests / second".format(NUMBER_OF_TIMES_TO_BUILD / total_time))
    sys.stdout.flush()


if __name__ == "__main__":
    request = stormhttp.HttpRequest()
    parser = stormhttp.HttpParser(request)
    parser.feed_data(RAW_REQUEST)
    total_time = 0

    for _ in range(NUMBER_OF_TIMES_TO_BUILD):
        start_time = time.time()  # --- START TIMER ---
        request.to_bytes()
        end_time = time.time()    # --- STOP TIMER ----
        total_time += (end_time - start_time)

    report(total_time)
