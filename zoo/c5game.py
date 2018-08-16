import requests
from bs4 import BeautifulSoup

from prototypes.DataPatch import DataPatch
from prototypes.ErrorTraceback import ErrorTraceback
from prototypes.Probe import Probe


class C5Probe(Probe):
    def __init__(self, **options):
        Probe.__init__(self, default_timeout=5, **options)
        self.type = 'C5Probe'

    def fetch_data(self, hash_name, timeout=None, target_func='bref', **options):
        if not timeout:
            timeout = self.options['default_timeout']
        self._log(7, f':fetch data:{hash_name}')
        if target_func in 'bref_info':
            return self.bref_info(hash_name, self.proxy, timeout=timeout)
        elif target_func in 'sales_info':
            return self.sales_info(hash_name, self.proxy, timeout=timeout)

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

    def sales_info(self, hash_name, proxy, timeout):
        try:
            base = 'https://www.c5game.com/dota.html?min=&max=&k='
            response = requests.get(base + str(hash_name), proxies=proxy, timeout=timeout)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                for li in soup.find_all(attrs={'class': 'purchaseing'}):
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
