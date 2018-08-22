from prototypes.Cell import Cell


class Cluster(Cell):
    def __init__(self, inner=None, cells=None):
        super().__init__(inner)
        if not cells:
            cells = []
        for cell in cells:
            cell.universe = self.universe
            cell._input = cell.input = self._input
            cell.output = self.output
            cell.fail = self.fail
        self._Cells = cells

    def activate(self, enable_log=True):
        for x in self._inners:
            x.activate(enable_log)
        for c in self._Cells:
            c.activate(enable_log=False)
        if enable_log:
            self.log(7, f':{self.__class__.__name__} activated.')

    def freeze(self, enable_log=True):
        for x in self._inners:
            x.freeze(enable_log)
        for c in self._Cells:
            c.freeze(enable_log=False)
        if enable_log:
            self.log(7, f':{self.__class__.__name__} frozen.')

    def state(self):
        if all([x.state() == 'frozen' for x in self._Cells]):
            ret = 'frozen'
        elif any([x.state() == 'processing' for x in self._Cells]):
            ret = 'processing'
        else:
            ret = 'waiting'
        if ret == 'waiting' and any([x.state() == 'processing' for x in self._inners]):
            return 'processing'
        return ret


if __name__ == '__main__':
    from models.Requestor import Requestor
    from models.Resolver import Resolver
    from zoo.c5game import C5game

    req_core = {
        'url': C5game.url,
        'hash_key': C5game.hash_key,
        'timeout': 1,
    }
    _req = Cluster(cells=[Requestor(**req_core) for x in range(10)])
    _res = Resolver(_req, resolve_func=C5game.resolve_func)

    r = _res
    r.universe.activate()
    r.activate()

    for i in range(20):
        r.input.put({'k': 'Astral Drift'})
    for i in range(20):
        print(r.output.get())

    r.freeze()
    r.universe.freeze()
