import time
from random import random

from prototypes.Cell import Cell


class Reducer(Cell):
    """
        base prototype to limit data flow.
        input & output: raw data
    """

    def __init__(self, inner=None, **reducer_settings):
        super().__init__(inner)
        self.set(interval=2.5, randomed=True, amplitude=0.3)
        self.set(**reducer_settings)

    def _service(self):
        interval = self.indiv('interval')
        randomed = self.indiv('randomed')
        amplitude = self.indiv('amplitude')
        while True:
            data = self._input.get()
            if randomed:
                interval += interval * amplitude * random()
            time.sleep(interval)
            self.output.put(data)
