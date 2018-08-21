import time
from random import random

from trashbin.Layer import Layer


class Reducer(Layer):
    """
        base prototype to limit data flow.
        input & output: raw data
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id='', **kwargs):
        super().__init__(input_layer, input, output, message_collector, id)
        self.set(interval=2.5, randomed=True, amp=0.3)
        self.set(**kwargs)

    def _service(self):
        while True:
            data = self.input.get()
            interval = self.indiv('interval')
            if self.indiv('randomed'):
                interval += interval * self.indiv('amp') * random()
            time.sleep(interval)
            self.output.put(data)
