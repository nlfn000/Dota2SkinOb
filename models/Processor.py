from prototypes.Cell import Cell


class Processor(Cell):
    def __init__(self, inner=None, process_func=lambda x: x):
        super().__init__(inner)
        self.set(process_func=process_func)

    def _service(self):
        process_func = self.indiv('process_func')
        while True:
            data = self._input.get()
            data = process_func(data)
            self.output.put(data)
