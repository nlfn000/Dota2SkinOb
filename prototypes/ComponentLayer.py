import queue

from prototypes.EmptyMessageCollector import EmptyCollector
from prototypes.Service import Service


class ComponentLayer(Service):
    """
        basic Layer prototype.
        input & output: queue typed flow.
    """

    def __init__(self, input_layer=None, message_collector=None):
        super().__init__()
        self.input = input_layer.output if input_layer else queue.Queue()
        if message_collector:
            self.message = message_collector
        elif input_layer:
            self.message = input_layer.message
        else:
            self.message = EmptyCollector()
        self.output = queue.Queue()

    def log(self, m_type, message):
        self.message.put((m_type, message))

    def _service(self):
        while True:
            data = self.input.get()  # just a pipe now
            self.output.put(data)

    def activate(self):
        super().activate()
        self.log(1, f':{self.__class__.__name__} activated.')

    def freeze(self):
        super().freeze()
        self.log(1, f':{self.__class__.__name__} frozen.')
