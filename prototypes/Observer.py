import queue
from typing import List, Any

from prototypes.Probe import *
from prototypes.ProxyPool import ProxyPool
from utils.proxies import conceal_proxies
from utils.inst_probes import *
from secrets.login_settings import *


class Observer(object):
    proxy_pool: ProxyPool
    probe_cluster: List[Any]

    def __init__(self, ProbeType=Probe, max_probes=7, **settings):

        self.task_queue = queue.Queue()
        self.feedback_queue = queue.Queue()
        self.failed_queue = queue.Queue()

        self.proxy_pool = None
        self.__alive = threading.Lock()
        self.activate(ProbeType=ProbeType, max_probes=max_probes, **settings)

    def activate(self, ProbeType, max_probes, enable_proxy=True, collect_func=conceal_proxies, **settings):
        if enable_proxy:
            self.proxy_pool = ProxyPool(collect_func=collect_func, **settings)
        self.probe_cluster = [
            ProbeType(task_queue=self.task_queue,
                      feedback_queue=self.feedback_queue,
                      failed_queue=self.failed_queue,
                      proxy_pool=self.proxy_pool,
                      code=code, **settings) for code in range(max_probes)]
        t = threading.Thread(target=self._service)
        t.start()

    def freeze(self):
        if self.proxy_pool:
            self.proxy_pool.freeze()
        if self.__alive.locked():
            self.__alive.release()

    def _service(self):
        self.__alive.acquire()
        for probe in self.probe_cluster:
            probe.setDaemon(True)
            probe.start()
        if self.__alive.acquire():
            print('\033[0;36m:probes turned off.\033[0m')
            self.__alive.release()

    def auth(self, **options):
        for probe in self.probe_cluster:
            probe.auth(**options)

    def join(self):
        self.task_queue.join()
        print(f'\033[0;36m:observer:all task joined.\033[0m')
        self.freeze()

    def request(self, hash_name=None, shuffle_proxies=False, **options):
        options['hash_name'] = hash_name
        options['shuffle_proxies'] = shuffle_proxies
        self.task_queue.put(options)

    def reap(self):
        ret = []
        while not self.feedback_queue.empty():
            ret.append(self.feedback_queue.get())
        return ret


if __name__ == '__main__':
    ob = Observer(ProbeType=SteamProbe, enable_proxy=False)
    ob.auth(steamLoginSecure=steamLoginSecure, sessionid=sessionid)
    ob.request(hash_name='Astral Drift', target_func='history', timeout=1)
    ob.join()
    print(ob.reap())
