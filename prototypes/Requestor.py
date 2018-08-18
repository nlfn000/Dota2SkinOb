import requests

from prototypes.ComponentLayer import ComponentLayer


class Requestor(ComponentLayer):
    def __init__(self, input_layer=None, message_collector=None, **kwargs):
        super().__init__(input_layer, message_collector)
        self.set(params={}, timeout=15)
        self.set(**kwargs)

    def _service(self):
        while True:
            keys = self.input.get()
            response = self.request(**keys)
            if response.status_code == 200:
                self.output.put(response)

    def request(self, **keys):
        url = self.indiv('url')
        params = dict(self.indiv('params'))
        params.update(keys)
        timeout = self.indiv('timeout')
        return requests.get(url=url, params=params, timeout=timeout)


if __name__ == '__main__':
    pass
