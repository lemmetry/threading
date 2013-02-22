import string
import urllib.request
from bs4 import BeautifulSoup
import queue
import threading


def getAlphabetUrls():
    pattern = 'http://www.nhl.com/ice/playersearch.htm?letter='
    return [(pattern + letter + '&pg=1') for letter in [char for char in string.ascii_uppercase]]


class ThreadAlphabetUrls(threading.Thread):
    def __init__(self, alphabet_queue):
        threading.Thread.__init__(self)
        self.alphabet_queue = alphabet_queue

    def run(self):
        while True:
            url = self.alphabet_queue.get()
            print(url)
            self.alphabet_queue.task_done()


alphabet_urls = getAlphabetUrls()

alphabet_queue = queue.Queue()

for _ in range(len(alphabet_urls)):
    t1 = ThreadAlphabetUrls(alphabet_queue)
    t1.setDaemon(True)
    t1.start()

for alphabet_url in alphabet_urls:
    alphabet_queue.put(alphabet_url)

alphabet_queue.join()