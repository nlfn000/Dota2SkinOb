import requests

from models.reducer import Reducer
from prototypes.Cell import Cell
from prototypes.Exceptions import UrlNotSetException
from models.retryer import Retryer


class Requestor(Cell):
    """
        extra input: key params for requesting
        output < hash & response (if status_code == 200)
        fail < keys
    """

    def __init__(self, inner=None, **req_core):
        super().__init__(inner)
        self.set(params={}, timeout=15)
        self.set(**req_core)

    def _service(self):
        while True:
            keys = self._input.get()
            response = self.request(**keys)
            if response and response.status_code == 200:
                self.output.put((keys.get('hash'), response))
            else:
                self.fail.put(keys)

    def request(self, **keys):
        url = self.indiv('url')
        params = dict(self.indiv('params'))
        params.update(keys)
        timeout = self.indiv('timeout')
        try:
            if not url:
                raise UrlNotSetException
            response = requests.get(url=url, params=params, timeout=timeout)
            return response
        except Exception as e:
            self.log_exception(e)


class ProxiedRequestor(Requestor):
    """
        proxied requestor prototype.
        must have a ProxyPool.
    """


if __name__ == '__main__':
    core = {
        'url': 'http://www.baidu.com'
    }
    r = Requestor(**core)
    r = Reducer(r, interval=1)
    a = Retryer(r)
    r.forced_inner(a)

    r.universe.activate()
    r.activate()

    r.fail.put({'hash': 123})
    r.input.put({'hash': 123})
    r.input.put({'hash': 123})
    r.input.put({'hash': 123})
    print(r.output.get())
    print(r.output.get())
    print(r.output.get())
    print(r.output.get())
    r.freeze()
    r.universe.freeze()
