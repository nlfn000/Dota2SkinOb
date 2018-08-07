import time
import threading

from prototypes.DataPatch import DataPatch


class Probe(threading.Thread):
    def __init__(self, task_queue, feedback_queue, failed_queue, proxy_pool, code='NaN',
                 max_retry=5, default_timeout=20, retry_interval=3, **settings):
        threading.Thread.__init__(self)

        self.type = 'ProtoType'
        self.code = code

        self.task_queue = task_queue
        self.feedback_queue = feedback_queue
        self.failed_queue = failed_queue

        self.proxy_pool = proxy_pool
        self.proxy = proxy_pool.get() if self.proxy_pool else None

        self._max_retry = max_retry
        self._default_timeout = default_timeout
        self._retry_interval = retry_interval

    def _shuffle_proxies(self):
        self.proxy = self.proxy_pool.next(self.proxy)
        print(f'\033[0;36m:Probe {self.code}:shuffled to {self.proxy}\033[0m')

    def _retry(self, **task):
        if self.proxy_pool:
            self.proxy = self.proxy_pool.get()
            print(f'\033[0;31m:Probe {self.code}:proxy abandoned:shuffled to {self.proxy}\033[0m')
        time.sleep(self._retry_interval)
        return self.fetch_data(**task)

    def run(self):
        print(f'\033[0;36m:Probe {self.code} activated.:type-{self.type}\033[0m')
        while True:
            task = self.task_queue.get()
            if task.get('shuffle_proxies') and self.proxy_pool:
                self._shuffle_proxies()
            patch = self.fetch_data(**task)
            retry = self._max_retry
            while patch.lost() and retry > 0:
                retry -= 1
                patch = self._retry(**task)
            if patch.valid():
                self.feedback_queue.put(patch.data())
            else:
                self.failed_queue.put((task, patch))
                print(f'\033[0;31m:Probe {self.code}:task failed with {patch.message()}.\033[0m')
            self.task_queue.task_done()

    def fetch_data(self, **options):
        """
        replace this func with custom method.
        """
        print(f'\033[0;32m:working on{str(options)}\033[0m')
        patch = DataPatch(options)
        print(f'\033[0;32m:data fetched:{patch}\033[0m')
        return patch

    def auth(self, **options):
        print(f'\033[0;32m:authorizing with:{options}\033[0m')
        pass
