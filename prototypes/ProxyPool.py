import queue
import threading
import time

from prototypes.LogEnabled import LogEnabled
from prototypes.OptionsEnabled import OptionsEnabled
from prototypes.Service import Service
from utils.proxies import conceal_proxies


class ProxyPool(OptionsEnabled, Service, LogEnabled, queue.Queue):
    def __init__(self, collect_func=conceal_proxies):
        OptionsEnabled.__init__(self)
        Service.__init__(self)
        LogEnabled.__init__(self)
        queue.Queue.__init__(self)
        self.settings(pool_lower_limit=0, pool_retry_interval=5)
        self.collect_func = collect_func
        self.__occupied = threading.Semaphore(1)

    def occupy(self):
        self.__occupied.acquire(blocking=False)

    def free(self):
        self.__occupied.release()
        if self.__occupied.acquire(blocking=False):
            self.freeze()
            self.__occupied.release()

    def next(self, used_proxy=None):
        proxy = self.get()
        if used_proxy:
            self.put(used_proxy)
        return proxy

    def _service(self, **supply_options):
        self._log(6, ':proxy pool activated.')
        super(ProxyPool, self)._service(target=self._auto_supply, kwargs=supply_options)
        self._log(6, ':proxy pool frozen.')

    def _auto_supply(self, **supply_options):
        while True:
            if self.qsize() <= self.options['pool_lower_limit']:
                proxies = self.collect_func(**supply_options)
                if proxies:
                    for p in proxies:
                        self.put(p)
                else:
                    self._log(1, ':failed to collect proxies.')
                    time.sleep(self.options['pool_retry_interval'])


if __name__ == '__main__':
    a = ProxyPool()
    print(a.options)
    print(a.is_frozen())
