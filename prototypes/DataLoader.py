import json

from prototypes.Cell import Cell
from prototypes.Exceptions import IllegalJsonException
from utils.ErrorReceiver import handle_error


class DataLoader(Cell):
    def __init__(self, file_path, load_func=lambda x: x, ):
        super().__init__()
        self.set(load_func=load_func, file_path=file_path)

    def _service(self):
        self._read(self.indiv('file_path'))

    def _read(self, file_path):
        with open(file_path, 'r')as f:
            for line in f.readlines():
                try:
                    data = json.loads(line)
                    data = self.indiv('load_func')(data)
                except IllegalJsonException:
                    handle_error(IllegalJsonException)
                else:
                    self.output.put(data)
