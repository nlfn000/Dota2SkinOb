from prototypes.Cell import Cell


class Retryer(Cell):
    """
        basic retryer prototype.
    """

    def __init__(self, inner=None, proxy_pool=None, **retryer_settings):
        super().__init__()
        if inner:
            self.connect(inner)
        if proxy_pool:
            self.proxy_pool = proxy_pool
        self.set(max_retry=5)
        self.set(**retryer_settings)
        self.retry_table = {}

    def connect(self, cell):
        self._input = cell.fail
        self.universe = cell.universe

    def _service(self):
        while True:
            _hash, task = self._input.get()
            self.proxy_pool.shuffle()
            self.log(1, f'-retry/{self.__class__.__name__}:{_hash}')
            if _hash in self.retry_table.keys():
                self.retry_table[_hash] += 1
            else:
                self.retry_table[_hash] = 1
            if self.retry_table[_hash] > self.indiv('max_retry'):
                continue
            self.output.put(task)
