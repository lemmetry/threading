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



def getSameInitialPlayersUrls(url):
    players_urls = []
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
        return players_urls + getSameInitialPlayersUrls(next_page)
    elif result_left_off == result_total:
        return players_urls
    else:
        print('something went wrong')


alphabet_urls = getAlphabetUrls()

alphabet_queue = queue.Queue()


for _ in range(len(alphabet_urls)):
    t1 = ThreadAlphabetUrls(alphabet_queue)
    t1.setDaemon(True)
    t1.start()

for alphabet_url in alphabet_urls:
    alphabet_queue.put(alphabet_url)

alphabet_queue.join()