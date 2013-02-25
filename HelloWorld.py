import string
import urllib.request
from bs4 import BeautifulSoup
import time
import queue
import threading

def getAlphabetUrls():
    pattern = 'http://www.nhl.com/ice/playersearch.htm?letter='
    return [(pattern + letter + '&pg=1') for letter in [char for char in string.ascii_uppercase]]

alphabet_urls = getAlphabetUrls()
alphabet_urls_queue = queue.Queue()


class ThreadAlphabetUrls(threading.Thread):
    def __init__(self, url_queue):
        self.url_queue = url_queue
        threading.Thread.__init__(self)

    def run(self):
        while True:
            url = self.url_queue.get()
            self.getSameInitialPlayersUrls(url)
            self.url_queue.task_done()
            

    def getSameInitialPlayersUrls(self, url):
        # will port function here
        print(url)


for url in alphabet_urls:
    alphabet_urls_queue.put(url)


threads = []
while alphabet_urls_queue.qsize() > 0:
    print(alphabet_urls_queue.qsize())
    for _ in range(5):
        t = ThreadAlphabetUrls(alphabet_urls_queue)
        t.start()
        threads.append(t)
    [t.join() for t in threads]

# never gets here
print(t.isAlive())
