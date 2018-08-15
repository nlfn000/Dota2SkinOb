import re

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
        self._log(7, f':fetch data:{hash_name}')
        if not timeout:
            timeout = self.options['default_timeout']
        if target_func in 'bref_info':
            return self.bref_info(hash_name, self.proxy, timeout=timeout)
        elif target_func in 'sales_info':
            return self.sales_info(hash_name, self.proxy, timeout=timeout)

    def bref_info(self, hash_name, proxy, timeout):
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
                self._log(6, ':DSApi.bref_info:item not found')
                return DataPatch(status_code=0)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            self._log(6, f':DSApi.bref_info:{response.status_code}')
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
        Probe.__init__(self, default_timeout=5, **options)
        self.type = 'C5Probe'

    def fetch_data(self, hash_name, timeout=None, **options):
        if not timeout:
            timeout = self.options['default_timeout']
        self._log(7, f':fetch data:{hash_name}')
        return self.bref_info(hash_name, self.proxy, timeout)

    def bref_info(self, hash_name, proxy, timeout):
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
                self._log(6, ':C5Probe.bref_info:item not found')
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
            timeout = self.options['default_timeout']
        self._log(7, f':fetch data:{hash_name}:on func {target_func}')
        if 'history' in target_func:
            return self.req_pricehistory(hash_name=hash_name, proxies=self.proxy, timeout=timeout)
        elif 'overview' in target_func:
            return self.req_priceoverview(hash_name=hash_name, proxies=self.proxy, timeout=timeout)
        elif 'detail' in target_func:
            return self.req_search(proxies=self.proxy, timeout=timeout, **options)
        elif 'order' in target_func:
            return self.req_itemordershistogram(hash_name=hash_name, proxies=self.proxy, timeout=timeout)
        elif 'nameid' in target_func:
            return self.get_item_nameid(hash_name, proxies=self.proxy, timeout=timeout)

    def req_pricehistory(self, hash_name, **req_options):
        try:
            url = 'http://steamcommunity.com/market/pricehistory/'
            params = {
                'country': 'JP',
                'currency': 1,
                'appid': 570,
                'market_hash_name': hash_name,
            }
            response = requests.get(url, params, cookies=self.login_auth, **req_options)
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
            self._log(1, f':bad response:{response.status_code}')
            return DataPatch(status_code=response.status_code)

    def req_priceoverview(self, hash_name, appid=570, **req_options):
        try:
            url = 'https://steamcommunity.com/market/priceoverview/'
            params = {
                'country': 'JP',
                'currency': 1,
                'appid': appid,
                'market_hash_name': hash_name,
            }
            response = requests.get(url, params, **req_options)
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
            self._log(1, f':bad response:{response.status_code}')
            return DataPatch(status_code=response.status_code)

    def req_search(self, start=0, size=100, sort_column='name', **req_options):
        try:
            url = 'https://steamcommunity.com/market/search/render/'
            params = {
                'appid': 570,
                'norender': 1,
                'sort_column': sort_column,
                'start': start,
                'count': size,
            }
            response = requests.get(url, params, **req_options)
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
            self._log(1, f':bad response:{response.status_code}')
            change_server()
            return DataPatch(status_code=response.status_code)

    def req_itemordershistogram(self, hash_name=None, item_nameid=None, **req_options):
        try:
            if not item_nameid:
                if not hash_name:
                    raise NameError
                item_nameid = self.get_item_nameid(hash_name, **req_options).data()['item_nameid']
            url = 'https://steamcommunity.com/market/itemordershistogram'
            params = {
                'country': 'CN',
                'language': 'schinese',
                'currency': 23,
                'norender': 1,
                'item_nameid': item_nameid,
                'two_factor': 0,
            }
            response = requests.get(url, params, **req_options)
            if response.status_code == 200:
                data = response.json()
                if data:
                    data['hash_name'] = hash_name
                    data['item_nameid'] = item_nameid
                    return DataPatch(data)
                return DataPatch(status_code=0)
        except Exception as e:
            ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            print(response.url)
            self._log(1, f':bad response:{response.status_code}')
            change_server()
            return DataPatch(status_code=response.status_code)

    def get_item_nameid(self, hash_name, **req_options):
        try:
            url = 'https://steamcommunity.com/market/listings/570/' + hash_name
            response = requests.get(url, **req_options)
            if response.status_code == 200:
                html = response.text
                tar = re.search(r'Market_LoadOrderSpread\( (.*?) \)', html)
                tar = tar.group(1)
                return DataPatch({'hash_name': hash_name, 'item_nameid': tar})
        except Exception as e:
            if 'AttributeError' in repr(e):
                print(f'\033[0;31m:{hash_name} item_nameid not found.\033[0m')
            else:

                ErrorTraceback(e)
            return DataPatch(status_code=1)
        else:
            self._log(1, f':bad response:{response.status_code}')
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
    p = SteamProbe()
    data = p.req_itemordershistogram('Codicil of the Veiled Ones')
    print(data.data())
