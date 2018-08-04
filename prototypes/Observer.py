import json
import os
import threading
import queue
import time

from forex_python.converter import CurrencyRates

from prototypes.Probe import Probe, DSProbe, C5Probe, SteamProbe
from utils.conceal_proxies import get_proxies
from prototypes.ErrorTraceback import ErrorTraceback


class Observer(object):

    def __init__(self, ProbeType=Probe, max_probes=20, disable_proxy=True, proxy_oversea=False, max_retry=15, **kwargs):

        self.current_rate = None
        self.task_queue = queue.Queue()
        self.feedback_queue = queue.Queue()
        self.failed_queue = queue.Queue()
        self.backup_proxies = queue.Queue()

        self.__wait2sleep = threading.Lock()
        self.__need2fill = threading.Lock()

        self.disable_proxy = disable_proxy
        self.proxy_oversea = proxy_oversea

        self.probe_cluster = [
            ProbeType(self.task_queue, self.feedback_queue, self.failed_queue,
                      disable_proxy=self.disable_proxy, fill_lock=self.__need2fill, backup_proxies=self.backup_proxies,
                      code=code, max_retry=max_retry, **kwargs)
            for code in range(max_probes)]

        t = threading.Thread(target=self.awaken)
        t.start()

    def awaken(self):
        if not self.disable_proxy:
            t = threading.Thread(target=self._auto_refill_proxies)
            t.setDaemon(True)
            t.start()
        for probe in self.probe_cluster:
            probe.setDaemon(True)
            probe.start()
        self.__wait2sleep.acquire()
        if self.__wait2sleep.acquire():
            print('\033[0;36m:probes turned off.\033[0m')
            self.__wait2sleep.release()

    def sleep(self):
        self.__wait2sleep.release()

    def _auto_refill_proxies(self):
        while True:
            if self.__need2fill.acquire():
                print('\033[0;36m:refilling backup proxies.\033[0m')
                for p in get_proxies(proxy_oversea=self.proxy_oversea):
                    self.backup_proxies.put(p)

    def request(self, hash_name, timeout=15, data_only=False, shuffle_proxies=True, **kwargs):
        self.task_queue.put(
            {'hash_name': hash_name, 'timeout': timeout, 'data_only': data_only, 'shuffle_proxies': shuffle_proxies,
             '**kwargs': kwargs})

    def reap(self):
        ret = []
        while not self.feedback_queue.empty():
            data = self.feedback_queue.get()
            ret.append(data)
        return ret

    def normalized_price(self, price_text, currency_type='CNY'):
        """
        simple currency convert toolkit
        :param price_text:
        :param currency_type:
        :return:
        """
        try:
            if not self.current_rate:
                print('\033[0;36m:fetching currency rate.\033[0m')
                self.current_rate = CurrencyRates().get_rates('CNY')
                self.current_rate['CNY'] = 1.0
            currency = {'$': 'USD',
                        'USD': 'USD',
                        '￥': 'CNY',
                        '¥': 'CNY',
                        'CNY': 'CNY'}
            if currency_type is not 'CNY':
                self.current_rate = CurrencyRates().get_rates(currency_type)
            price_text = price_text.replace(' ', '').replace('\'', '')
            for prefix in currency:
                if prefix in price_text:
                    currency_type = currency[prefix]
                price_text = price_text.replace(prefix, '')
            price = float(price_text) / self.current_rate[currency_type]
            return price
        except Exception as e:
            ErrorTraceback(e)


if __name__ == '__main__':
    pass
