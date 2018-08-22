import queue
import threading
import time

from prototypes.Cell import Cell
from prototypes.Exceptions import FailedToCollectException
from utils.proxies import conceal_proxies


class ProxyPool(Cell):
    """
        input: request task
        output: request task with proxies

        the pool is auto maintained at a certain quantity.
    """

    def __init__(self, inner=None, collect_func=conceal_proxies):
        super().__init__(inner)
        self.set(pool_lower_limit=10,
                 pool_retry_interval=5,
                 collect_func=collect_func,
                 pages=5,
                 rate=0.3, )
        self._dry = threading.Event()
        self._proxies = queue.Queue()
        self.proxy = None

    def _get(self):
        if self._proxies.qsize() <= self.indiv('pool_lower_limit'):
            self._dry.set()
        return self._proxies.get()

    def _current_proxy(self):
        if not self.proxy:
            self.proxy = self._get()
        return self.proxy

    def shuffle(self):
        self.proxy = self._get()

    def _service_thread(self):
        self._frozen.clear()
        t1 = threading.Thread(target=self._auto_refill)
        t1.setDaemon(True)
        t1.start()
        t2 = threading.Thread(target=self._service)
        t2.setDaemon(True)
        t2.start()
        self._frozen.wait()

    def _service(self):
        while True:
            task = self._input.get()
            task['proxies'] = self._current_proxy()
            self.output.put(task)

    def _auto_refill(self):
        while True:
            self._dry.wait()
            pages = self.indiv('pages')
            rate = self.indiv('rate')
            try:
                proxies = self.indiv('collect_func')(pages=pages, rate=rate)
                if proxies:
                    for p in proxies:
                        self._proxies.put(p)
                    self._dry.clear()
            except FailedToCollectException as e:
                self.universe.log_exception(e)
                time.sleep(self.indiv('pool_retry_interval'))
