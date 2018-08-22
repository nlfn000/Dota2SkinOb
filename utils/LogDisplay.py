import queue
import time

from prototypes.Service import Service


class LogDisplay(Service):
    def __init__(self):
        super().__init__()
        self.message = queue.Queue()

    def activate(self):
        super().activate()
        print(':Logs on.')

    def freeze(self):
        while self.message.qsize() > 0:  # wait for clearing logs
            time.sleep(1)
        super().freeze()
        print(':Logs off.')

    def put(self, package):
        self.message.put(package)

    @staticmethod
    def log_bar(*args):
        colors = [2, 4, 7, 1]
        shapes = ['▂', '▅', '▃', '▁']
        bar = ''
        for idx, arg in enumerate(args):
            arg = int(arg * 30)
            bar += f'\033[0;3{colors[idx]}m' + arg * shapes[idx] + '\033[0m'
        print(bar)

    def _service(self):
        while True:
            color, op = self.message.get()
            print(f'\033[0;3{color}m{op}\033[0m')


if __name__ == '__main__':
    dis = LogDisplay()
    dis.log_bar(0.1, 0.3, 0.4, 0.2)
