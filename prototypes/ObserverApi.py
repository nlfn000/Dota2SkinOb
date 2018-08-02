import threading
import queue
from forex_python.converter import CurrencyRates


class ObserverApi:

    def __init__(self, state=None):
        self.state = state
        self.ret_collector = []
        self.ret_queue = queue.Queue()
        self.mutex = threading.Lock()
        self.current_rate = CurrencyRates().get_rates('CNY')
        self.current_rate['CNY'] = 1.0

    def info(self, hash_name, timeout=5):
        """

        :param hash_name: MarketHashName of items
        :param timeout:
        :return: {hash,status,data} and {status} if failed
        """
        try:
            t = threading.Thread(target=self.__get_info, args=[hash_name])
            t.start()
            t.join(timeout=timeout)
            while not self.ret_queue.empty():
                if self.mutex.acquire():
                    self.ret_collector.append(self.ret_queue.get())
                    self.mutex.release()
            for ret in self.ret_collector:
                if ret['hash'] == t.getName():
                    if self.mutex.acquire():
                        self.ret_collector.remove(ret)
                        self.mutex.release()
                        return ret
        except:
            return {'status': ':ObserverApi.info:fail'}

    def __get_info(self, hash_name):
        try:
            self.ret_queue.put({'hash': threading.current_thread().getName(),
                                'status': 200,
                                'data': ':Proto:GetInfo(' + hash_name + ')'})
        except:
            print({'status': ':ObserverApi.__get_info:fail'})

    def normalized_price(self, price_text, currency_type='CNY'):
        """

        :param price_text: just price text(
        :param currency_type: the benchmark of normalization
        :return: float type and {status} if failed
        """
        try:
            currency = {'$': 'USD',
                        'USD': 'USD',
                        '￥': 'CNY',
                        'CNY': 'CNY'}
            if currency_type is not 'CNY':
                self.current_rate = CurrencyRates().get_rates(currency_type)
            price_text = price_text.replace(' ', '')
            for prefix in currency:
                if prefix in price_text:
                    currency_type = currency[prefix]
                price_text = price_text.replace(prefix, '')
            price = float(price_text) / self.current_rate[currency_type]
            return price
        except:
            return {'status': ':ObserverApi.normalized_price:fail'}

