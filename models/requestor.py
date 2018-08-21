import requests
from prototypes.ToyBrick import ToyBrick
from prototypes.Exceptions import UrlNotSetException


class Requestor(ToyBrick):
    """
        input: key params for requesting
        output: keys & response (if status_code == 200)
    """

    def __init__(self, inner=None, *forced_inners, **req_core):
        super().__init__(inner, *forced_inners)
        self.set(params={}, timeout=15)
        self.set(**req_core)

    def _service(self):
        while True:
            keys = self.input.get()
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
    r = Requestor(r)
    r.universe.activate()
    r.activate()
    # r.input.put({'hash': 123})
    # print(r.output.get())
    r.freeze()
    r.universe.freeze()
