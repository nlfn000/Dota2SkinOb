import queue
import time

from prototypes.OptionsEnabled import OptionsEnabled
from prototypes.Service import Service


class MessageDisplay(Service, OptionsEnabled, queue.Queue):
    def __init__(self):
        Service.__init__(self)
        OptionsEnabled.__init__(self)
        queue.Queue.__init__(self)
        self.settings(color_separation=True, quest_message=True)

    def activate(self):
        if self._is_frozen():
            super().activate()

    def freeze(self):
        while self.qsize() > 0:
            time.sleep(1)
        super(MessageDisplay, self).freeze()

    def _service(self, **supply_options):
        print(':Message Display on.')
        super(MessageDisplay, self)._service(target=self._display, **supply_options)
        print(':Message Display off.')

    def _display(self, **supply_options):
        self.settings(**supply_options)
        color_separation = self.options['color_separation']
        quest_message = self.options['quest_message']
        while True:
            color, op = self.get()
            if not quest_message and color == 7:
                continue
            if color_separation:
                print(f'\033[0;3{color}m:{op}\033[0m')
            else:
                print(op)


if __name__ == '__main__':
    dis = MessageDisplay()
    print(dis.options)
    print(dis.is_frozen())
