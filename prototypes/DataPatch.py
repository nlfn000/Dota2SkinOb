from collections import defaultdict


class DataPatch:
    def __init__(self, data=None, status_code=200):
        self._status_code = int(status_code)
        self._data = data

    def __str__(self):
        return f'<Response[{self._status_code}]>'

    def lost(self):
        return not (self._status_code == 200 or self._status_code == 0)

    def valid(self):
        return self._status_code == 200

    def data(self):
        if self._status_code == 200:
            return self._data
        return self.message()

    def data_dict_(self):
        if self._data:
            return self._data
        else:
            return {}

    def not_found(self):
        return self._status_code == 0

    def message(self):
        message = defaultdict(lambda: self.__str__())
        message[0] = '<NotFound>'
        message[1] = '<RuntimeError>'
        return message[self._status_code]
