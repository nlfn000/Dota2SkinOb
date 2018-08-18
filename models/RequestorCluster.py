from prototypes.Layer import CompressedLayer
from prototypes.Requestor import Requestor


class RequestorCluster(CompressedLayer):
    """
        clustered multi-threading requestors.
    """
    def __init__(self, input_layer=None, input=None, output=None, message_collector=None,
                 scale=10, requestor_type=Requestor):
        super().__init__(input_layer, input, output, message_collector)
        requestors = [requestor_type(input=self.input, output=self.output, message_collector=self.message, id=str(i))
                      for i in range(scale)]
        self.layers = requestors
