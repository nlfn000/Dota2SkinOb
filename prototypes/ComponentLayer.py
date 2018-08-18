import queue

from prototypes.Service import Service
from utils.MessageDisplay import MessageDisplay


class ComponentLayer(Service):
    def __init__(self, input_layer=None, message_collector=None):
        super().__init__()
        self.input = input_layer.output if input_layer else queue.Queue()
        self.message = input_layer.message if not message_collector else message_collector.message
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


if __name__ == '__main__':
    dis = MessageDisplay()
    c = ComponentLayer(message_collector=dis)
    dis.activate()
    c.activate()
    c.freeze()
    dis.freeze()
