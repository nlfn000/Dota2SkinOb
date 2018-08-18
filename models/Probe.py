from bs4 import BeautifulSoup

from prototypes.Layer import CompressedLayer
from prototypes.Requestor import Requestor
from prototypes.Resolver import Resolver


class Probe(CompressedLayer):
    """
        tracker for refine data from single sites.
        structure:
            [requestor] >> [resolver]
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id=''):
        super().__init__(input_layer, input, output, message_collector, id)

        requestor = Requestor(input=self.input, message_collector=self.message, id=id)  # build the net
        requestor.set(url='http://www.baidu.com')
        resolver = Resolver(requestor, output=self.output, id=id)

        self.requestor = requestor
        self.resolver = resolver
        layers = [requestor, resolver]
        self.layers = layers
