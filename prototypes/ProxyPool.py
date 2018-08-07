import queue
import threading
import time


class ProxyPool(queue.Queue):
    def __init__(self, collect_func, **supply_options):
        queue.Queue.__init__(self)
        self.get_proxies = collect_func
        self.__alive = threading.Lock()
        self.activate(**supply_options)

    def restart(self, **supply_options):
        self.freeze()
        time.sleep(0.05)
        self.activate(**supply_options)

    def activate(self, **supply_options):
        t = threading.Thread(target=self._service, kwargs=supply_options)
        t.start()

    def freeze(self):
        if self.__alive.locked():
            self.__alive.release()

    def next(self, used_proxy=None):
        proxy = self.get()
        if used_proxy:
            self.put(used_proxy)
        return proxy

    def _service(self, **supply_options):
        self.__alive.acquire()
        print('\033[0;36m:proxy pool activated.\033[0m')
        t = threading.Thread(target=self._auto_supply, kwargs=supply_options)
        t.setDaemon(True)
        t.start()
        if self.__alive.acquire():
            print('\033[0;36m:proxy pool frozen.\033[0m')
            self.__alive.release()

    def _auto_supply(self, pool_lower_limit=0, pool_retry_interval=5, **supply_options):
        while True:
            if self.qsize() <= pool_lower_limit:
                proxies = self.get_proxies(**supply_options)
                if proxies:
                    for p in proxies:
                        self.put(p)
                else:
                    print('\033[0;31m:failed to collect proxies.\033[0m')
                    time.sleep(pool_retry_interval)


if __name__ == '__main__':
    pass
