import json
import os

from prototypes.Cell import Cell


class DataSaver(Cell):
    def __init__(self, inner, file_path, save_func=lambda x: x):
        super().__init__(inner)
        self.set(save_func=save_func, file_path=file_path, reveal_data=True)

    @staticmethod
    def create_if_not_exist(path):
        _folder, _file = '/'.join(path.split('/')[0:-1]) + '/', path.split('/')[-1]
        if not os.path.exists(_folder):
            os.makedirs(_folder)
        if not os.path.exists(path):
            open(path, 'w')

    def _service(self):
        file_path = self.indiv('file_path')
        save_func = self.indiv('save_func')
        self.create_if_not_exist(file_path)
        while True:
            data = self._input.get()
            self._save(file_path, data, save_func)
            self.output.put(data)

    def _save(self, file_path, data, save_func):
        with open(file_path, 'a') as f:
            try:
                data = save_func(data)
                data = json.dumps(data)
                f.write(data + '\n')
            except Exception as e:
                self.universe.log_exception(e)
