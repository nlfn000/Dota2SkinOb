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
        self.set(interval=2.5, randomed=True, amp=0.3)
        self.set(**reducer_settings)

    def _service(self):
        while True:
            data = self._input.get()
            interval = self.indiv('interval')
            if self.indiv('randomed'):
                interval += interval * self.indiv('amp') * random()
            time.sleep(interval)
            self.output.put(data)
