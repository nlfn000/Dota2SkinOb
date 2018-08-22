import requests
from prototypes.Cell import Cell
from prototypes.Exceptions import UrlNotSetException


class Requestor(Cell):
    """
        extra input: key params for requesting
        output < hash & response (if status_code == 200)
        fail < hash & keys
    """

    def __init__(self, inner=None, **req_core):
        super().__init__(inner)
        self.set(params={}, timeout=15, hash_key='hash_name')
        self.set(**req_core)

    def _service(self):
        hash_key = self.indiv('hash_key')
        while True:
            task = self._input.get()
            response = self._request(**task)
            _h = task.get(hash_key)
            if response and response.status_code == 200:
                self.output.put((_h, response))
            else:
                self.fail.put((_h, task))

    def _request(self, proxies=None, **keys):
        url = self.indiv('url')
        params = dict(self.indiv('params'))
        params.update(keys)
        timeout = self.indiv('timeout')
        try:
            if not url:
                raise UrlNotSetException
            response = requests.get(url=url, params=params, timeout=timeout, proxies=proxies)
            return response
        except Exception as e:
            self.log_exception(e)
