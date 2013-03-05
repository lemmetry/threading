import string
import queue
import threading
import urllib.request
from bs4 import BeautifulSoup
# from time import time, sleep


def getABCUrls():
    pattern = 'http://www.nhl.com/ice/playersearch.htm?letter='
    return [(pattern + letter + '&pg=1') for letter in
            [char for char in string.ascii_uppercase]]


class ABCThread(threading.Thread):
    def __init__(self, abc_urls_queue, abc_queue_condition, players_queue,
                 players_queue_condition):
        threading.Thread.__init__(self)
        self.abc_urls_queue = abc_urls_queue
        self.abc_queue_condition = abc_queue_condition
        self.players_queue = players_queue
        self.players_queue_condition = players_queue_condition

    def run(self):
        while True:
            self.abc_queue_condition.acquire()
            try:
                if not self.abc_urls_queue.empty():
                    abc_url = self.abc_urls_queue.get()
                    self.abc_urls_queue.task_done()
                else:
                    break
            finally:
                self.abc_queue_condition.notify_all()
                self.abc_queue_condition.release()
            sameInitialPlayersUrls = self.getSameInitialPlayersUrls(abc_url)
            print(self.getName(), abc_url, len(sameInitialPlayersUrls))

            with self.players_queue_condition:
                [self.players_queue.put(url) for url in sameInitialPlayersUrls]

    def getSameInitialPlayersUrls(self, alphabet_url):
        players_urls = []

        url = alphabet_url
        link = urllib.request.urlopen(url)
        soup = BeautifulSoup(link.read())

        if soup.find('div', {
            'style': 'padding: 6px; font-weight: bold;'}) is not None:
            return players_urls

        for l in soup.find_all('a'):
            candidate = l.get('href')
            candidate = str(candidate)
            if ('http' not in candidate) and (
                    candidate not in players_urls) and (
                    '/ice/player.htm?id' in candidate):
                players_urls.append(
                    'http://www.nhl.com' + candidate + '&view=splits')

        node = soup.find('div', {'class': 'resultCount'}).next
        results = node.split()
        result_left_off = int(results[0].split('-')[1])
        result_total = int(results[2])

        if result_left_off < result_total:
            next_page = url[:url.rfind('=') + 1] + str(
                result_left_off // 50 + 1)
            return players_urls + self.getSameInitialPlayersUrls(next_page)
        elif result_left_off == result_total:
            return players_urls
        else:
            print('something went wrong')


def main():
    print('main started')

    abc_urls = getABCUrls()
    abc_urls_queue = queue.Queue()
    [abc_urls_queue.put(url) for url in abc_urls]
    abc_queue_condition = threading.Condition(threading.RLock())

    players_queue = queue.Queue()
    players_queue_condition = threading.Condition(threading.RLock())

    abc_threads = [
        ABCThread(abc_urls_queue, abc_queue_condition, players_queue,
                  players_queue_condition) for _ in range(5)]
    [t.start() for t in abc_threads]
    [t.join() for t in abc_threads]

    print(players_queue.qsize())
    print('main finished')


main()