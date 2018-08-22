from prototypes.Cell import Cell


class Resolver(Cell):
    """
        input: hash & response
        output: resolved data
    """

    def __init__(self, inner=None, resolve_func=lambda _h, _r: _r):
        super().__init__(inner)
        self.set(resolve_func=resolve_func)

    def _service(self):
        resolve_func = self.indiv('resolve_func')
        while True:
            _hash, response = self._input.get()
            resolved = resolve_func(_hash, response)
            self.output.put(resolved)

