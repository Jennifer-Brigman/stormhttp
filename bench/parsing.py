import stormhttp
import time

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

NUMBER_OF_TIMES_TO_PARSE = 1000000

if __name__ == "__main__":
    parser = stormhttp.HttpParser()

    print("Starting benchmark for parsing {} requests.".format(NUMBER_OF_TIMES_TO_PARSE))
    total_time = 0

    for _ in range(NUMBER_OF_TIMES_TO_PARSE):
        parser.set_target(stormhttp.HttpRequest())
        start_time = time.time()  # --- START TIMER ---
        parser.feed_data(RAW_REQUEST)
        end_time = time.time()    # --- STOP TIMER ----
        total_time += (end_time - start_time)

    print("Parsed {0} requests in {1:.4f} seconds.".format(NUMBER_OF_TIMES_TO_PARSE, total_time))
    print("Achieved an average of {0:.4f}ms per parsed request.".format((total_time) * 1000 / NUMBER_OF_TIMES_TO_PARSE))

    print("Starting benchmark for parsing {} responses.".format(NUMBER_OF_TIMES_TO_PARSE))
    total_time = 0

    for _ in range(NUMBER_OF_TIMES_TO_PARSE):
        parser.set_target(stormhttp.HttpResponse())
        start_time = time.time()  # --- START TIMER ---
        parser.feed_data(RAW_RESPONSE)
        end_time = time.time()    # --- STOP TIMER ----
        total_time += (end_time - start_time)

    print("Parsed {0} responses in {1:.4f} seconds.".format(NUMBER_OF_TIMES_TO_PARSE, total_time))
    print("Achieved an average of {0:.4f}ms per parsed response.".format((total_time) * 1000 / NUMBER_OF_TIMES_TO_PARSE))
