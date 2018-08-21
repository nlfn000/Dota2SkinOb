import queue
import time
from trashbin.Layer import Layer
from prototypes.Exceptions import FailedToCollectException
from utils.ErrorReceiver import handle_error
from utils.LogDisplay import LogDisplay
from utils.proxies import conceal_proxies


class ProxyPool(Layer):
    """
        input: None
        output: proxies (maintained at a certain quantity)
    """

    def __init__(self, collect_func=conceal_proxies):
        super().__init__(message_collector=LogDisplay())  # private logger
        self.set(pool_lower_limit=0,
                 pool_retry_interval=5,
                 collect_func=collect_func,
                 pages=5,
                 rate=0.3, )
        self.proxies = queue.Queue()
        self.output = self.proxies

    def activate(self):
        self.message.activate()
        super().activate()

    def freeze(self):
        super().freeze()
        self.message.freeze()

    def get(self):
        return self.proxies.get()

    def put(self, proxy):
        self.proxies.put(proxy)

    def shuffle(self, proxy):
        self.put(proxy)
        return self.get()

    def _service(self):
        while True:
            if self.proxies.qsize() <= self.indiv('pool_lower_limit'):
                pages = self.indiv('pages')
                rate = self.indiv('rate')
                try:
                    proxies = self.indiv('collect_func')(pages=pages, rate=rate)
                    if proxies:
                        for p in proxies:
                            self.put(p)
                except FailedToCollectException as e:
                    handle_error(e)
                    time.sleep(self.indiv('pool_retry_interval'))
