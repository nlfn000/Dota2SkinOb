from prototypes.Cell import Cell


class Retryer(Cell):
    """
        basic retryer prototype.

    """

    def __init__(self, inner=None, **retryer_settings):
        super().__init__()
        if inner:
            self.connect(inner)
        self.set(max_retry=5, hash_key='hash_name')
        self.set(**retryer_settings)
        self.retry_table = {}

    def connect(self, cell=None, *cells):
        cells = list(cells)
        if cell:
            cells.append(cell)
        for x in cells:
            x.fail = self._input
            x.universe = self.universe

    def _service(self):
        while True:
            task = self._input.get()
            _hash = task.get(self.indiv('hash_key'))
            self.log(1, f'-retry/{self.__class__.__name__}:{_hash}')
            if _hash in self.retry_table.keys():
                self.retry_table[_hash] += 1
            else:
                self.retry_table[_hash] = 1
            if self.retry_table[_hash] > self.indiv('max_retry'):
                continue
            self.output.put(task)
