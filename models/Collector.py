from models.Processor import Processor
from models.ProxyPool import ProxyPool
from models.Reducer import Reducer
from models.Requestor import Requestor
from models.Resolver import Resolver
from models.Retryer import Retryer
from prototypes.Cell import Cell
from prototypes.Cluster import Cluster


class SingleCollector(Cell):
    """
        This is a single-requestor 'Collector' module for collecting and resolving data.
        structure:
            [reducer] -> ([proxy pool]) -> [requestor] -> [resolver]
               \               |                 /
                \<-------- [retryer] <---------/

    """

    def __init__(self, inner=None, interval=1, resolve_func=lambda _h, _r: _r, enable_proxy=False, **_req_core):
        self._Reducer = Reducer(inner=inner, interval=interval)
        if enable_proxy:
            self._ProxyPool = ProxyPool(self._Reducer)
            self._Requestor = Requestor(self._ProxyPool, **_req_core)
            self._Retryer = Retryer(self._Requestor, self._ProxyPool)
        else:
            self._Requestor = Requestor(self._Reducer, **_req_core)
            self._Retryer = Retryer(self._Requestor)
        self._Reducer.join_input(self._Retryer)
        self._Resolver = Resolver(self._Requestor, resolve_func=resolve_func)

        super().__init__(inner)
        self.universe = self._Resolver.universe
        self._input = self.input = self._Resolver.input
        self.output = self._Resolver.output
        self.fail = self._Resolver.fail

    def activate(self, enable_log=True):
        for x in self._inners:
            x.activate(enable_log)
        self._Resolver.activate(enable_log=False)
        if enable_log:
            self.log(7, f':{self.__class__.__name__} activated.')

    def freeze(self, enable_log=True):
        for x in self._inners:
            x.freeze(enable_log)
        self._Resolver.freeze(enable_log=False)
        if enable_log:
            self.log(7, f':{self.__class__.__name__} frozen.')

    def state(self):
        ret = self._Resolver.state()
        if ret == 'waiting' and any([x.state() == 'processing' for x in self._inners]):
            return 'processing'
        return ret


class ClusteredCollector(Cell):
    """
        This is a requestors-clustered version 'Collector'.
        structure:
            [reducer] -> ([proxy pool]) -> *[cluster/requestor] -> [resolver]
               \               |                 /
                \<-------- [retryer] <---------/

    """

    def __init__(self, inner=None, size=10, interval=1.0, resolve_func=lambda _h, _r: _r, enable_proxy=True,
                 **_req_core):
        self._Reducer = Reducer(inner=inner, interval=interval)
        if enable_proxy:
            self._ProxyPool = ProxyPool(self._Reducer)
            self._RequestorCluster = Cluster(self._ProxyPool, cells=[Requestor(**_req_core) for x in range(size)])
            self._Retryer = Retryer(self._RequestorCluster, self._ProxyPool)
        else:
            self._RequestorCluster = Cluster(self._Reducer, cells=[Requestor(**_req_core) for x in range(size)])
            self._Retryer = Retryer(self._RequestorCluster)
        self._Reducer.join_input(self._Retryer)
        self._Resolver = Resolver(self._RequestorCluster, resolve_func=resolve_func)

        super().__init__(inner)
        self.universe = self._Resolver.universe
        self._input = self.input = self._Resolver.input
        self.output = self._Resolver.output
        self.fail = self._Resolver.fail

    def activate(self, enable_log=True):
        for x in self._inners:
            x.activate(enable_log)
        self._Resolver.activate(enable_log=False)
        if enable_log:
            self.log(7, f':{self.__class__.__name__} activated.')

    def freeze(self, enable_log=True):
        for x in self._inners:
            x.freeze(enable_log)
        self._Resolver.freeze(enable_log=False)
        if enable_log:
            self.log(7, f':{self.__class__.__name__} frozen.')

    def state(self):
        ret = self._Resolver.state()
        if ret == 'waiting' and any([x.state() == 'processing' for x in self._inners]):
            return 'processing'
        return ret


if __name__ == '__main__':
    from zoo.c5game import C5game
    from models.DataSaver import DataSaver
    from models.DataLoader import DataLoader
    import time

    core = {
        'url': C5game.url,
        'hash_key': C5game.hash_key,
        'resolve_func': C5game.resolve_func,
        'timeout': 1,
        'interval': 0.01,
    }
    DL = DataLoader('../data/item_description.json', load_func=lambda x: {C5game.hash_key: x['hash_name']})
    s = SingleCollector(DL, enable_proxy=False, **core)
    s = DataSaver(s, '../data/tmp/trash/savor.json')

    s.universe.tasks = DL.output
    s.universe.receiver = s.output
    s.universe.activate()
    s.activate()

    time.sleep(5)
    s.universe.join()

    s.freeze()
    s.universe.freeze()
