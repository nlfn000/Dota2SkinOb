import requests
from bs4 import BeautifulSoup

from prototypes.DataPatch import DataPatch
from prototypes.ErrorTraceback import ErrorTraceback
from prototypes.Probe import Probe
from script.shadowsocks import change_server


class DSProbe(Probe):
    def __init__(self, **options):
        Probe.__init__(self, **options)
        self.type = 'DSProbe'

    def fetch_data(self, hash_name, timeout=None, target_func='bref', **kwargs):
        print(f'\033[0;37m:fetch data:{hash_name}\033[0m')
        if not timeout:
            timeout = self._default_timeout
        if target_func in 'bref_info':
            return self.bref_info(hash_name, self.proxy, timeout=timeout)
        elif target_func in 'sales_info':
            return self.sales_info(hash_name, self.proxy, timeout=timeout)

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
                json = response.json()
                items = json.get('MerchandiseList')
                for item in items:
                    hash_n = item['MarketHashName']
                    if hash_n == hash_name:
                        return DataPatch({'hash_name': hash_name,
                                          'Price': item['LocalPrice'],
                                          'TotalCount': json['TotalCount']})
                print('\033[0;36m:DSApi.bref_info:item not found\033[0m')
                return DataPatch(status_code=0)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            print(f'\033[0;36m:DSApi.bref_info:{response.status_code}\033[0m')
            return DataPatch(status_code=response.status_code)

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
                data = response.json()
                sale_info = data.get('SaleInfo')
                if not sale_info:
                    return DataPatch(status_code=0)
                return DataPatch({'hash_name': hash_name, 'sales': [x['PriceCNYString'] for x in sale_info]})
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            return DataPatch(status_code=response.status_code)


class C5Probe(Probe):
    def __init__(self, **options):
        Probe.__init__(self, **options)
        self.type = 'C5Probe'

    def fetch_data(self, hash_name, timeout=None, **options):
        if not timeout:
            timeout = self._default_timeout
        print(f'\033[0;37m:fetch data:{hash_name}\033[0m')
        return self.bref_info(hash_name, self.proxy, timeout)

    @staticmethod
    def bref_info(hash_name, proxy, timeout):
        try:
            base = 'https://www.c5game.com/dota.html?min=&max=&k='
            response = requests.get(base + str(hash_name), proxies=proxy, timeout=timeout)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                for li in soup.find_all(attrs={'class': 'selling'}):
                    name = li.find('span').text.strip()
                    num = li.find(attrs={'class': 'num'}).text.split(' ')[0]
                    price_text = li.find(attrs={'class': 'price'}).text
                    if name == hash_name:
                        return DataPatch({'hash_name': hash_name,
                                          'OnSale': num,
                                          'Price': price_text})
                print('\033[0;36m:C5Probe.bref_info:item not found\033[0m')
                return DataPatch(status_code=0)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            return DataPatch(status_code=response.status_code)


class SteamProbe(Probe):

    # sessionid = '74e1e50281794c2992253bde'
    # steamLoginSecure = '76561198123694279||52C968EA888227E78C5F75999986A746F1866044'

    def __init__(self, session_id=None, steam_login_secure=None, **options):
        Probe.__init__(self, **options)
        self.login_auth = {'sessionid': session_id, 'steamLoginSecure': steam_login_secure}

    def auth(self, steamLoginSecure, sessionid=None, **kwargs):
        self.login_auth['steamLoginSecure'] = steamLoginSecure
        self.login_auth['sessionid'] = sessionid if sessionid else self.login_auth['sessionid']

    def fetch_data(self, hash_name=None, target_func='overview', timeout=None, **options):
        if not timeout:
            timeout = self._default_timeout
        print(f'\033[0;37m:fetch data:{hash_name}:on func {target_func}\033[0m')
        if 'history' in target_func:
            return self.price_history(hash_name=hash_name, login_auth=self.login_auth, proxy=self.proxy,
                                      timeout=timeout)
        elif 'overview' in target_func:
            return self.price_overview(hash_name=hash_name, proxy=self.proxy, timeout=timeout)
        elif 'detail' in target_func:
            return self.item_detail(proxy=self.proxy, timeout=timeout, **options)

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
            if response.status_code == 200:
                data = response.json()
                if len(data) == 0:
                    return DataPatch(status_code=0)
                data = {'hash_name': hash_name, 'data': data}
                return DataPatch(data)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            print(f'\033[0;31m:bad response:{response.status_code}\033[0m')
            return DataPatch(status_code=response.status_code)

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
            response = requests.get(url, params, timeout=timeout, proxies=proxy)
            if response.status_code == 200:
                data = response.json()
                if len(data) == 0:
                    return DataPatch(status_code=0)
                data['hash_name'] = hash_name
                return DataPatch(data)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            print(f'\033[0;31m:bad response:{response.status_code}\033[0m')
            return DataPatch(status_code=response.status_code)

    @staticmethod
    def item_detail(start=0, size=100, proxy=None, sort_column='name', timeout=20, **kwargs):
        try:
            url = 'https://steamcommunity.com/market/search/render/'
            params = {
                'appid': 570,
                'norender': 1,
                'sort_column': sort_column,
                'start': start,
                'count': size,
            }
            response = requests.get(url, params, timeout=timeout, proxies=proxy)
            if response.status_code == 200:
                data = response.json()
                data = data.get('results')
                if data:
                    return DataPatch(data)
                return DataPatch(status_code=0)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            print(f'\033[0;31m:bad response:{response.status_code}\033[0m')
            change_server()
            return DataPatch(status_code=response.status_code)

    @staticmethod
    def get_total_count():
        url = 'https://steamcommunity.com/market/search/render/?appid=570&norender=1&sort_column=name'
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data['total_count']


if __name__ == '__main__':
    pass
