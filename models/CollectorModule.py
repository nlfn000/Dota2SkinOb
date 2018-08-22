from models.proxies import ProxyPool
from models.reducer import Reducer
from models.requestor import Requestor
from models.resolver import Resolver
from models.retryer import Retryer
from prototypes.Cell import Cell
from prototypes.Cluster import Cluster


class SingleCollector(Cell):
    def __init__(self, inner=None, interval=1, resolve_func=lambda _h, _r: _r, **_req_core):
        self._Reducer = Reducer(inner=inner, interval=interval)
        self._ProxyPool = ProxyPool(self._Reducer)
        self._Requestor = Requestor(self._ProxyPool, **_req_core)
        self._Retryer = Retryer(self._Requestor, self._ProxyPool)
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
    def __init__(self, inner=None, size=10, interval=1.0, resolve_func=lambda _h, _r: _r, **_req_core):
        self._Reducer = Reducer(inner=inner, interval=interval)
        self._ProxyPool = ProxyPool(self._Reducer)
        self._RequestorCluster = Cluster(self._ProxyPool, cells=[Requestor(**_req_core) for x in range(size)])
        self._Retryer = Retryer(self._RequestorCluster, self._ProxyPool)
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

    req_core = {
        'url': C5game.url,
        'hash_key': C5game.hash_key,
        'timeout': 0.5,
    }
    # s = SingleCollector(resolve_func=C5game.resolve_func, **req_core)
    s = ClusteredCollector(interval=0.01, resolve_func=C5game.resolve_func, **req_core)
    s.universe.activate()
    s.activate()

    s.input.put({'k': 'Astral Drift'})
    s.input.put({'k': 'Axe'})
    s.input.put({'k': 'Astral Drift'})

    print(s.output.get())
    print(s.output.get())
    print(s.output.get())

    s.freeze()
    s.universe.freeze()
