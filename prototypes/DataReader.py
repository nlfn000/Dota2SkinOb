import json

from prototypes.Exceptions import IllegalJsonException
from prototypes.Layer import Layer
from utils.ErrorReceiver import handle_error


class DataReader(Layer):
    def __init__(self, load_func=lambda x: x, output=None, message_collector=None, id=''):
        super().__init__(output=output, message_collector=message_collector, id=id)
        self.set(load_func=load_func)

    def read(self, file_path):
        with open(file_path, 'r')as f:
            for line in f.readlines():
                try:
                    data = json.loads(line)
                    data = self.indiv('load_func')(data)
                except IllegalJsonException:
                    handle_error(IllegalJsonException)
                else:
                    self.output.put(data)
