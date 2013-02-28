import string
import queue
import threading
import urllib.request
from bs4 import BeautifulSoup
from time import time


def getAlphabetUrls():
    pattern = 'http://www.nhl.com/ice/playersearch.htm?letter='
    return [(pattern + letter + '&pg=1') for letter in [char for char in string.ascii_uppercase]]


class MyThread(threading.Thread):
    def __init__(self, alphabet_urls_queue, players_urls):
        self.alphabet_urls_queue = alphabet_urls_queue
        self.players_urls = players_urls
        self.lock = threading.RLock()

        threading.Thread.__init__(self)

    def run(self):
        while not self.alphabet_urls_queue.empty():
            alphabet_url = self.alphabet_urls_queue.get()
            sameInitialPlayersUrls = self.getSameInitialPlayersUrls(alphabet_url)

            self.lock.acquire()
            self.players_urls.extend(sameInitialPlayersUrls)
            self.lock.release()

            self.alphabet_urls_queue.task_done()

    def getSameInitialPlayersUrls(self, alphabet_url):
        # print('%s will work on %s here' % (self.getName(), alphabet_url))
        # sleep(1)
        players_urls = []

        url = alphabet_url
        link = urllib.request.urlopen(url)
        soup = BeautifulSoup(link.read())

        if soup.find('div', {'style': 'padding: 6px; font-weight: bold;'}) is not None:
            return players_urls

        for l in soup.find_all('a'):
            candidate = l.get('href')
            candidate = str(candidate)
            if ('http' not in candidate) and (candidate not in players_urls) and ('/ice/player.htm?id' in candidate):
                players_urls.append('http://www.nhl.com' + candidate + '&view=splits')

        node = soup.find('div', {'class': 'resultCount'}).next
        results = node.split()
        result_left_off = int(results[0].split('-')[1])
        result_total = int(results[2])

        if result_left_off < result_total:
            next_page = url[:url.rfind('=') + 1] + str(result_left_off // 50 + 1)
            return players_urls + self.getSameInitialPlayersUrls(next_page)
        elif result_left_off == result_total:
            return players_urls
        else:
            print('something went wrong')



def main():
    print('main started')
    for num_of_threads in range(2, 27):
        num_of_simulations = 50
        start = time()
        for i in range(num_of_simulations):
            alphabet_urls = getAlphabetUrls()
            players_urls = []

            alphabet_urls_queue = queue.Queue()
            [alphabet_urls_queue.put(url) for url in alphabet_urls]

            threads = [MyThread(alphabet_urls_queue, players_urls) for _ in range(num_of_threads)]
            [t.start() for t in threads]
            [t.join() for t in threads]
        total_time = time() - start
        print('%d threads: %d simulations in %d sec. %d sec per simulation. list check: %d' % (num_of_threads, num_of_simulations, total_time, total_time / num_of_simulations, len(players_urls)))
    print('main finished')
main()