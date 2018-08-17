import queue
import time

from prototypes.ComponentLayer import ComponentLayer
from utils.MessageDisplay import MessageDisplay


class Requestor(ComponentLayer):
    def __init__(self, *args):
        super().__init__(*args)

    def _service(self):
        while True:
            data = self.input.get()
            print(data)
            self.output.put(data)


if __name__ == '__main__':
    dis = MessageDisplay()

    c = ComponentLayer(message_collector=dis)
    r = Requestor(c)
    dis.activate()
    c.activate()
    r.activate()

    tasks = c.input

    tasks.put(1)
    tasks.put(2)
    time.sleep(2)
    tasks.put(3)
    time.sleep(0.5)

    c.freeze()
    r.freeze()
    dis.freeze()
