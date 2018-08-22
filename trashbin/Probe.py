from trashbin.Layer import CompressedLayer
from models.Requestor import Requestor, ProxiedRequestor
from models.Resolver import Resolver


class Probe(CompressedLayer):
    """
        tracker for refine data from single sites.
        structure:
            [requestor] >> [resolver]
    """

    def __init__(self, input_layer=None, input=None, output=None, proxy_pool=None, message_collector=None, id=''):
        super().__init__(input_layer, input, output, message_collector, id)

        if proxy_pool:
            requestor = ProxiedRequestor(input=self.input, message_collector=self.message, id=id, proxy_pool=proxy_pool)
        else:
            requestor = Requestor(input=self.input, message_collector=self.message, id=id)  # build the net
        requestor.set(url='http://www.baidu.com')
        resolver = Resolver(requestor, output=self.output, id=id)

        self.requestor = requestor
        self.resolver = resolver
        layers = [requestor, resolver]
        self.layers = layers
