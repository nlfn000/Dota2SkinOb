import queue
import time

from prototypes.Service import Service


class MessageDisplay(Service):
    def __init__(self):
        super().__init__()
        self.message = queue.Queue()

    def activate(self):
        super().activate()
        print(':MessageDisplay on.')

    def freeze(self):
        while self.message.qsize() > 0:  # wait for clearing logs
            time.sleep(1)
        super().freeze()
        print(':MessageDisplay off.')

    def put(self, *args):
        self.message.put(*args)

    def _service(self):
        while True:
            color, op = self.message.get()
            print(f'\033[0;3{color}m:{op}\033[0m')


if __name__ == '__main__':
    dis = MessageDisplay()
