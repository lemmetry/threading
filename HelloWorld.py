import string
import queue
import threading

def getAlphabetUrls():
    pattern = 'http://www.nhl.com/ice/playersearch.htm?letter='
    return [(pattern + letter + '&pg=1') for letter in [char for char in string.ascii_uppercase]]


class MyThread(threading.Thread):
    def __init__(self, alphabet_urls_queue):
        self.alphabet_urls_queue = alphabet_urls_queue
        threading.Thread.__init__(self)

    def run(self):
        alphabet_url = self.alphabet_urls_queue.get()
        self.getSameInitialPlayersUrls(alphabet_url)

    def getSameInitialPlayersUrls(self, alphabet_url):
        print('will work on %s here' %(alphabet_url))


def main():
    alphabet_urls = getAlphabetUrls()
    alphabet_urls_queue = queue.Queue()

    [alphabet_urls_queue.put(url) for url in alphabet_urls]

    while alphabet_urls_queue.qsize() > 0:
        size = alphabet_urls_queue.qsize()
        if size > 5:
            threads = [MyThread(alphabet_urls_queue) for _ in range(5)]
        else:
            threads = [MyThread(alphabet_urls_queue) for _ in range(size)]
        [t.start() for t in threads]
        [t.join() for t in threads]

    print('DONE')

main()