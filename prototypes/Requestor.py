import requests

from prototypes.Layer import Layer
from utils.EmptyCollector import EmptyCollector
from utils.ErrorReceiver import handle_error
from prototypes.Exceptions import UrlNotSetException


class Requestor(Layer):
    """
        input: key params for requesting
        output: keys & response (if status_code == 200)
    """

    def __init__(self, input_layer=None, input=None, output=None, feedback=None, message_collector=None, id='',
                 **kwargs):
        super().__init__(input_layer, input, output, message_collector, id)
        self.feedback = feedback if feedback else EmptyCollector()
        self.set(params={}, timeout=15)
        self.set(**kwargs)

    def _service(self):
        while True:
            keys = self.input.get()
            response = self.request(**keys)
            if response and response.status_code == 200:
                self.output.put((keys, response))
            else:
                self.feedback.put(keys)

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
            handle_error(e)


class ProxiedRequestor(Requestor):
    """
        proxied requestor prototype.
        must have a ProxyPool.
    """

    def __init__(self, proxy_pool, input_layer=None, input=None, output=None, feedback=None, message_collector=None,
                 id='', **kwargs):
        self.proxies = proxy_pool
        super().__init__(input_layer, input, output, feedback, message_collector, id, **kwargs)

    def request(self, **keys):
        url = self.indiv('url')
        params = dict(self.indiv('params'))
        params.update(keys)
        timeout = self.indiv('timeout')
        proxy = self.proxies.get()
        try:
            if not url:
                raise UrlNotSetException
            response = requests.get(url=url, params=params, timeout=timeout, proxies=proxy)
            return response
        except Exception as e:
            handle_error(e)
