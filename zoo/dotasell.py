import requests

from prototypes.DataPatch import DataPatch
from prototypes.ErrorTraceback import ErrorTraceback
from prototypes.Probe import Probe


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
                                          's_price': item['LocalPrice'],
                                          's_quantity': json['TotalCount']})
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
