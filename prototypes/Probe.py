import json
import time

import requests
import threading

from bs4 import BeautifulSoup

from prototypes.ErrorTraceback import ErrorTraceback
from utils.basic_bs4 import find_all_by_class, find_by_class

# try to push
class Probe(threading.Thread):
    def __init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies, code='NaN',
                 min_proxy_backup=10, max_retry=5, **kwargs):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.feedback_queue = feedback_queue
        self.failed_queue = failed_queue
        self._disable_proxy = disable_proxy
        self.fill_lock = fill_lock
        self.code = code
        self.backup_proxies = backup_proxies
        self.proxy = backup_proxies.get() if not backup_proxies.empty() else None
        self._min_proxy_backup = min_proxy_backup
        self.max_retry = max_retry
        self.type = 'ProtoType'
        self.request_timeout = 1

    def run(self):
        print(f'\033[0;36m:Probe {self.code} waked.:type-{self.type}\033[0m')
        while True:
            retry = self.max_retry
            chunk = self.task_queue.get()
            self._shuffle_proxies(chunk)
            data = self.fetch_data(chunk)
            while not data and retry > 0:
                retry -= 1
                data = self._re_fetch(chunk)
            if retry < 1:
                self.failed_queue.put(chunk)
                self.task_queue.task_done()
                continue
            self.feedback_queue.put(data)
            self.task_queue.task_done()

    def _re_fetch(self, chunk):
        if not self._disable_proxy:
            if self.backup_proxies.qsize() < self._min_proxy_backup and self.fill_lock.locked():
                self.fill_lock.release()
            self.proxy = self.backup_proxies.get()
            print(f'\033[0;31m:Probe {self.code}:proxy abandoned:shuffled to {self.proxy}\033[0m')
        time.sleep(3)
        return self.fetch_data(chunk)

    def _shuffle_proxies(self, chunk):
        if not self._disable_proxy and chunk['shuffle_proxies']:
            self.proxy = self.backup_proxies.get()
            self.backup_proxies.put(self.proxy)
            print(f'\033[0;36m:Probe {self.code}:shuffled to {self.proxy}\033[0m')

    def fetch_data(self, chunk):
        """
        replace this func with custom method.
        :param chunk: keywords of work.
        :return: info fetched,return None if not found.
        """
        print('working on' + str(chunk))
        return chunk


class DSProbe(Probe):
    def __init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies, code='NaN',
                 min_proxy_backup=10, max_retry=5):
        Probe.__init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies, code,
                       min_proxy_backup, max_retry)

    def fetch_data(self, chunk):
        hash_name = chunk['hash_name']
        proxy = self.proxy
        print(f'\033[0;37m:fetch data:{hash_name}\033[0m')
        kwargs = chunk['**kwargs']
        if 'bref' in kwargs.keys() and not kwargs['bref']:
            return self.sales_info(hash_name, proxy, timeout=self.request_timeout)
        else:
            return self.bref_info(hash_name, proxy, timeout=self.request_timeout)

    @staticmethod
    def bref_info(hash_name, proxy, timeout):
        try:
            req_data = {
                'appid': '570',
                'keyw': hash_name,
                'Sockets': '0',
                'start': '0',
                'fuzz': 'true',
                'AssetsType': '0',
                'OrderBy': 'Default',
                'safeonly': 'false'
            }
            base = 'http://www.dotasell.com/xhr/json_search.ashx'
            response = requests.get(base, params=req_data, proxies=proxy, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data and 'MerchandiseList' in data:
                    items = data['MerchandiseList']
                    for item in items:
                        hash_n = item['MarketHashName']
                        if hash_n == hash_name:
                            return {'MarketHashName': hash_name,
                                    'Price': item['LocalPrice'],
                                    'TotalCount': data['TotalCount']}
                print('\033[0;36m:DSApi.bref_info:item not found\033[0m')
            else:
                print(f'\033[0;36m:DSApi.bref_info:{response.status_code}\033[0m')
        except Exception as e:
            ErrorTraceback(e)

    @staticmethod
    def sales_info(hash_name, proxy, timeout):
        try:
            base_sales = 'http://www.dotasell.com/xhr/json_ItemsInSale.ashx?appid=570'
            req_data = {
                'GemNeedle': ['-1'],
                'HashName': hash_name,
                'onlytradable': 'True',
                'start': '0',
                'StyleNeedle': '-1'
            }
            response = requests.post(base_sales, json=req_data, proxies=proxy, timeout=timeout)
            if response:
                data = json.loads(response.text)
                sale_info = data.get('SaleInfo')
                return {'MarketHashName': hash_name, 'sales': [x['PriceCNYString'] for x in sale_info]}
        except Exception as e:
            ErrorTraceback(e)


class C5Probe(Probe):
    def __init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies, code='NaN',
                 min_proxy_backup=10, max_retry=5, **kwargs):
        Probe.__init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies, code,
                       min_proxy_backup, max_retry, **kwargs)

    def fetch_data(self, chunk):
        hash_name = chunk['hash_name']
        proxy = self.proxy
        print(f'\033[0;37m:fetch data:{hash_name}\033[0m')
        return self.bref_info(hash_name, proxy, self.request_timeout)

    @staticmethod
    def bref_info(hash_name, proxy, timeout):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        }
        try:
            base = 'https://www.c5game.com/dota.html?min=&max=&k='
            response = requests.get(base + str(hash_name), proxies=proxy, timeout=timeout, headers=headers)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                for li in find_all_by_class(soup, 'selling'):
                    name = li.find('span').text.strip()
                    num = li.find(attrs={'class': 'num'}).text.split(' ')[0]
                    price_text = find_by_class(li, 'price').text
                    if name == hash_name:
                        return {'MarketHashName': hash_name,
                                'OnSale': num,
                                'Price': price_text}
        except Exception as e:
            ErrorTraceback(e)


class SteamProbe(Probe):

    # sessionid = '74e1e50281794c2992253bde'
    # steamLoginSecure = '76561198123694279||52C968EA888227E78C5F75999986A746F1866044'

    def __init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies,
                 code='NaN', min_proxy_backup=10, max_retry=5, **kwargs):
        Probe.__init__(self, task_queue, feedback_queue, failed_queue, disable_proxy, fill_lock, backup_proxies,
                       code, min_proxy_backup, max_retry, **kwargs)
        session_id = kwargs.get('session_id')
        steam_login_secure = kwargs.get('steam_login_secure')
        self.login_auth = {'sessionid': session_id, 'steamLoginSecure': steam_login_secure}

    def refresh_auth(self, steam_login_secure, session_id=None):
        self.login_auth['steamLoginSecure'] = steam_login_secure
        self.login_auth['sessionid'] = session_id if session_id else self.login_auth['sessionid']

    def fetch_data(self, chunk):
        hash_name = chunk['hash_name']
        proxy = self.proxy
        info_type = 'unknown'
        if 'type' in chunk['**kwargs'].keys():
            info_type = chunk['**kwargs']['type']
        print(f'\033[0;37m:fetch data:{hash_name}:type {info_type}\033[0m')
        if 'history' in info_type:
            return self.price_history(hash_name=hash_name, login_auth=self.login_auth, proxy=proxy,
                                      timeout=self.request_timeout)
        elif 'histogram' in info_type:
            return self.orders_histogram(hash_name=hash_name, proxy=proxy,
                                         timeout=self.request_timeout)
        elif 'overview' in info_type:
            return self.price_overview(hash_name=hash_name, proxy=proxy,
                                       timeout=self.request_timeout)
        return self.price_overview(hash_name=hash_name, proxy=proxy,
                                   timeout=self.request_timeout)

    @staticmethod
    def price_history(hash_name, login_auth, timeout=20, appid=570, proxy=None):
        try:
            url = 'http://steamcommunity.com/market/pricehistory/'
            params = {
                'country': 'JP',
                'currency': 1,
                'appid': appid,
                'market_hash_name': hash_name,
            }
            response = requests.get(url, params, cookies=login_auth, timeout=timeout, proxies=proxy)
            data = json.loads(response.text)
            data = {'MarketHashName': hash_name, 'data': data}
            return data
        except Exception as e:
            ErrorTraceback(e)

    @staticmethod
    def price_overview(hash_name, timeout=20, appid=570, proxy=None):
        try:
            url = 'https://steamcommunity.com/market/priceoverview/'
            params = {
                'country': 'JP',
                'currency': 1,
                'appid': appid,
                'market_hash_name': hash_name,
            }
            # requests.session().keep_alive = True
            response = requests.get(url, params, timeout=timeout, proxies=proxy)
            if response.status_code == 200:
                data = json.loads(response.text)
                data['MarketHashName'] = hash_name
                return data
            print(f'\033[0;31m:bad response:{response.status_code}\033[0m')
        except Exception as e:
            ErrorTraceback(e)

    @staticmethod
    def orders_histogram(hash_name, timeout=20, appid=570, proxy=None):
        return 'not implemented'
        # try:
        #     url = 'https://steamcommunity.com/market/itemordershistogram/'
        #     params = {
        #         'country': 'JP',
        #         'currency': 1,
        #         'appid': appid,
        #         'market_hash_name': hash_name,
        #     }
        #     response = requests.get(url, params, timeout=timeout, proxies=proxy)
        #     data = json.loads(response.text)
        #     data['MarketHashName'] = hash_name
        #     return data
        # except Exception as e:
        #     ErrorTraceback(e)
