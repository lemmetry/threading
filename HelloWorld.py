from Queue import Queue
import string
import threading
from time import sleep

def getAlphabetUrls():
    pattern = 'http://www.nhl.com/ice/playersearch.htm?letter='
    return [(pattern + letter + '&pg=1') for letter in [char for char in string.ascii_uppercase]]

class MyThread(threading.Thread):
    def __init__(self, thread_name, alphabet_urls_queue):
        self.thread_name = thread_name
        self.alphabet_urls_queue = alphabet_urls_queue
        threading.Thread.__init__(self)

    def run(self):
        while not self.alphabet_urls_queue.empty():
            alphabet_url = self.alphabet_urls_queue.get()
            self.getSameInitialPlayersUrls(alphabet_url)
            self.alphabet_urls_queue.task_done()

    def getSameInitialPlayersUrls(self, alphabet_url):
        print '%s: will work on %s here' % (self.thread_name, alphabet_url)
        sleep(1)

def main():
    alphabet_urls = getAlphabetUrls()
    alphabet_urls_queue = Queue()

    [alphabet_urls_queue.put(url) for url in alphabet_urls]

    threads = [MyThread('Thread#%d' % (i + 1,), alphabet_urls_queue) for i in range(5)]
    [t.start() for t in threads]
    [t.join() for t in threads]


    print('DONE')

main()