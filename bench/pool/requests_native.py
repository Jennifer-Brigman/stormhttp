from multiprocessing import Pool
import requests
import time
import sys
import math

URL = "http://www.example.com"
NUMBER_OF_REQUESTS = 10000
NUMBER_OF_SESSIONS = int(math.ceil(math.sqrt(NUMBER_OF_REQUESTS)))


def report(total_time: float):
    sys.stdout.write("{0:.5f} requests / second".format(NUMBER_OF_REQUESTS / total_time))
    sys.stdout.flush()


if __name__ == "__main__":
    urls = [URL] * NUMBER_OF_REQUESTS
    with Pool(NUMBER_OF_SESSIONS) as p:
        start_time = time.time()  # --- START TIMER ---
        p.map(requests.get, urls)
        end_time = time.time()  # --- STOP TIMER ----

    report(end_time - start_time)
