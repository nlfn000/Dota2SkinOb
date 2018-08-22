from trashbin.Layer import CompressedLayer
from models.Requestor import Requestor
from utils.EmptyCollector import EmptyCollector


class RequestorCluster(CompressedLayer):
    """
        clustered multi-threading requestors.
        structure:
           >> [Requestor]*n >>
    """

    def __init__(self, input_layer=None, input=None, output=None, feedback=None, message_collector=None,
                 scale=10, requestor_type=Requestor):
        super().__init__(input_layer, input, output, message_collector)
        self.feedback = feedback if feedback else EmptyCollector()  # public feedback
        requestors = [
            requestor_type(input=self.input, output=self.output, feedback=self.feedback, message_collector=self.message,
                           id=str(i))
            for i in range(scale)]
        self.layers = requestors
