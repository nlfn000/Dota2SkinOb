import queue

from trashbin.SsServer import SsServer
from utils.LogDisplay import LogDisplay
from trashbin.Probe_depred import *
from prototypes.ProxyPool import ProxyPool
from prototypes.Service import Service
from utils.proxies import conceal_proxies
from zoo.c5game import C5Probe


class Observer(LogEnabled, Service):

    def __init__(self, probe_class=Probe, display_module=None, enable_proxy=True, max_probes=7, proxy_pool=None,
                 collect_func=conceal_proxies, **settings):
        LogEnabled.__init__(self, display_module=display_module)
        Service.__init__(self)

        # basic container
        self.task_queue = queue.Queue()
        self.failed_queue = queue.Queue()
        self.feedback_queue = queue.Queue()

        # basic connector
        self.probe_connector = []
        self.proxy_connector = None
        self.shadowsocks = SsServer()

        # initialize
        if not self.log:
            self.log = LogDisplay()
        if not proxy_pool and enable_proxy:
            proxy_pool = ProxyPool(collect_func=collect_func)  # create default proxy pool
        probes = [probe_class(code=i, **settings) for i in range(max_probes)]

        # link components
        self.link_proxy(proxy_pool)
        self.link_probe(probes)

        self.activate(enable_proxy=enable_proxy, **settings)

    def state(self):
        t, u, fail = self.task_queue.qsize(), self.task_queue.unfinished_tasks, self.failed_queue.qsize()
        self._log(2, f'{u-t}/{u} tasks processing:{fail} failed.')

    def activate(self, enable_proxy, color_separation=True, **settings):
        self.log.activate(color_separation=color_separation)
        if enable_proxy:
            if self.proxy_connector and self.proxy_connector.is_frozen():  # activate proxies if needed
                self.proxy_connector.activate(**settings)
            self.proxy_connector.occupy()
        super(Observer, self).activate(**settings)

    def _service(self, **supply_options):
        self._freeze.clear()
        for probe in self.probe_connector:  # activate all probes
            probe.setDaemon(True)
            probe.start()
        self._freeze.wait()  # till frozen
        self._log(6, ':probes turned off.')

    def freeze(self):
        self._leave(self.proxy_connector)
        super(Observer, self).freeze()
        self._log(6, ':observer shut down.')
        self.log.freeze()

    def auth(self, **options):
        for probe in self.probe_connector:
            probe.auth(**options)

    def join(self):
        self.task_queue.join()
        self._log(6, ':observer:all task joined.')
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

    @staticmethod
    def _leave(component):
        if component:
            component.free()

    def link_proxy(self, proxy_pool):
        if not proxy_pool:
            return
        proxy_pool.log = self.log
        proxy_pool.occupy()
        if self.proxy_connector:
            self._leave(self.proxy_connector)
        self.proxy_connector = proxy_pool
        for probe in self.probe_connector:
            probe.connect(self)

    def link_probe(self, probes):
        for probe in probes:
            probe.connect(self)
            self.probe_connector.append(probe)


if __name__ == '__main__':
    ob = Observer(probe_class=C5Probe)
    # ob = Observer(probe_class=SteamProbe, enable_proxy=False)
    # ob.auth(steamLoginSecure=steamLoginSecure, sessionid=sessionid)
    # ob.request(hash_name='Astral Drift', target_func='history', timeout=5)
    ob.request(hash_name='Astral Drift', target_func='entire')
    # ob.request(hash_name='A Bit of Boat')
    # ob.request(hash_name='Not Exist')

    ob.join()
    print(ob.reap())
