import queue
from functools import reduce

from prototypes.Exceptions import UncompressedLayerException
from utils.EmptyCollector import EmptyCollector
from prototypes.Service import Service


class LayerCore(Service):
    """
        basic Layer prototype.
        input & output: queue typed flow.
    """

    def __init__(self, input, output, message_collector, id):
        super().__init__()
        self.input = input
        self.output = output
        self.message = message_collector
        self.id = id

    def log(self, m_type, message):
        self.message.put((m_type, message))

    def _service(self):
        while True:
            data = self.input.get()  # just a pipe now
            self.output.put(data)

    def activate(self):
        super().activate()
        self.log(1, f':{self.__class__.__name__}<{self.id}> activated.')

    def freeze(self):
        super().freeze()
        self.log(1, f':{self.__class__.__name__}<{self.id}> frozen.')


class Layer(LayerCore):
    """
        arg wrapper for Layer, default values all been set.
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id=''):
        if input_layer:
            input = input_layer.output
            message_collector = input_layer.message
        if not input:
            input = queue.Queue()
        if not output:
            output = queue.Queue()
        if not message_collector:
            message_collector = EmptyCollector()
        super().__init__(input, output, message_collector, id)


class CompressedLayer(Layer):
    """
        basic prototype for compressed layer.
    """

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id=''):
        super().__init__(input_layer, input, output, message_collector, id)
        self.layers = []

    def is_frozen(self):
        return reduce(lambda x, y: x and y, [layer.is_frozen() for layer in self.layers])

    def activate(self):
        if len(self.layers) < 1:
            raise UncompressedLayerException
        self.log(1, f':{self.__class__.__name__}<{self.id}> activated.')
        for layer in self.layers:
            layer.activate()

    def freeze(self):
        for layer in self.layers:
            layer.freeze()
        self.log(1, f':{self.__class__.__name__}<{self.id}> frozen.')

    def set(self, **kwargs):
        for layer in self.layers:
            layer.set(**kwargs)
