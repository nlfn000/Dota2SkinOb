import re
import time

import requests

from prototypes.DataPatch import DataPatch
from utils.ErrorReceiver import handle_error
from trashbin.Probe_depred import Probe


def get_total_item_count():
    url = 'https://steamcommunity.com/market/search/render/?appid=570&norender=1&sort_column=name'
    response = requests.get(url, timeout=15)
    if response.status_code == 200:
        data = response.json()
        return data['total_count']


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
            handle_error(e)
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
            handle_error(e)
            return DataPatch(status_code=1)
        else:
            self._log(1, f':bad response:{response.status_code}')
            return DataPatch(status_code=response.status_code)

    def req_search(self, start=0, size=100, sort_column='name', proxies=None, timeout=10, **req_options):
        try:
            url = 'https://steamcommunity.com/market/search/render/'
            params = {
                'appid': 570,
                'norender': 1,
                'sort_column': sort_column,
                'start': start,
                'count': size,
            }
            response = requests.get(url, params, proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                data = data.get('results')
                if data:
                    return DataPatch(data)
                return DataPatch(status_code=0)
        except Exception as e:
            handle_error(e)
            return DataPatch(status_code=1)
        else:
            self._log(1, f':bad response:{response.status_code}')
            self.shadowsocks.shuffle_server()
            return DataPatch(status_code=response.status_code)

    def req_itemordershistogram(self, hash_name=None, item_nameid=None, **req_options):
        try:
            if not item_nameid:
                if not hash_name:
                    raise NameError
                item_nameid = self.get_item_nameid(hash_name, **req_options).data()['item_nameid']
                if item_nameid == 'NotFound':
                    raise NotImplementedError
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
            handle_error(e)
            return DataPatch(status_code=1)
        else:
            print(response.url)
            self._log(1, f':bad response:{response.status_code}')
            self.shadowsocks.shuffle_server()
            return DataPatch(status_code=response.status_code)

    def get_item_nameid(self, hash_name, **req_options):
        try:
            url = 'https://steamcommunity.com/market/listings/570/' + hash_name
            time.sleep(1)
            response = requests.get(url, **req_options)
            if response.status_code == 200:
                html = response.text
                tar = re.search(r'Market_LoadOrderSpread\( (.*?) \)', html)
                tar = tar.group(1)
                return DataPatch({'hash_name': hash_name, 'item_nameid': tar})
        except Exception as e:
            if 'AttributeError' in repr(e):
                print(f'\033[0;31m:{hash_name} item_nameid not found.\033[0m')
                return DataPatch({'hash_name': hash_name, 'item_nameid': 'NotFound'})
            else:
                handle_error(e)
            return DataPatch(status_code=1)
        else:
            self._log(1, f':bad response:{response.status_code}')
            self.shadowsocks.shuffle_server()
            return DataPatch(status_code=response.status_code)
