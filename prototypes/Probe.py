import time
import threading

from prototypes.DataPatch import DataPatch
from prototypes.ErrorTraceback import ErrorTraceback
from prototypes.LogEnabled import LogEnabled
from prototypes.OptionsEnabled import OptionsEnabled


class Probe(OptionsEnabled, LogEnabled, threading.Thread):
    def __init__(self, code='NaN', **settings):
        OptionsEnabled.__init__(self)
        LogEnabled.__init__(self)
        threading.Thread.__init__(self)
        # container
        self.task_queue, self.processing_queue, self.feedback_queue, self.failed_queue, self.proxy_pool = [None, None,
                                                                                                           None, None,
                                                                                                           None]
        self.probe_type = 'ProtoType'  # info
        self.code = code
        self.settings(max_retry=4, default_timeout=20, retry_interval=3)
        self.proxy = None
        self.shadowsocks = None

    def connect(self, observer):
        self.task_queue = observer.task_queue
        self.failed_queue = observer.failed_queue
        self.feedback_queue = observer.feedback_queue
        self.log = observer.log
        self.proxy_pool = observer.proxy_connector
        self.shadowsocks = observer.shadowsocks

    def _shuffle_proxies(self):
        self.proxy = self.proxy_pool.next(self.proxy)
        self._log(6, f':Probe {self.code}:shuffled to {self.proxy}')

    def _retry(self, **task):
        if self.proxy_pool:
            self.proxy = self.proxy_pool.get()
            self._log(1, f':Probe {self.code}:proxy abandoned:shuffled to {self.proxy}')
        time.sleep(self.options['retry_interval'])
        return self.fetch_data(**task)

    def run(self):
        self._log(6, f':Probe {self.code} activated.:type-{self.probe_type}')
        if self.proxy_pool:
            self._shuffle_proxies()
        while True:
            task = self.task_queue.get()
            if task.get('shuffle_proxies') and self.proxy_pool:
                self._shuffle_proxies()
            patch = self.fetch_data(**task)
            retry = self.options['max_retry']
            while patch.lost() and retry > 0:
                retry -= 1
                patch = self._retry(**task)
            if patch.valid():
                self.feedback_queue.put(patch.data())
            else:
                if task.get('hash_name') and patch.not_found():
                    self.feedback_queue.put({'hash_name': task['hash_name'], 'NotFound': True})
                else:
                    self.failed_queue.put(task)
                self._log(7, f':Probe {self.code}:task failed with {patch.message()}.')
            self.task_queue.task_done()

    def fetch_data(self, **options):
        """
        replace this func with custom method.
        """
        self._log(2, f':working on{str(options)}')

        try:
            patch = DataPatch(options)
        except Exception as e:
            ErrorTraceback(e)
            patch = DataPatch(status_code=450)

        self._log(2, f':data fetched:{patch}')
        return patch

    def auth(self, **options):
        self._log(2, f':authorizing with:{options}')


if __name__ == '__main__':
    # log = MessageDisplay()
    p = Probe(fuck=10)
    # p.log = log
    # log.activate()
    print(p.options)
    # log.freeze()
