from prototypes.ComponentLayer import ComponentLayer
from utils.MessageDisplay import MessageDisplay


class Requestor(ComponentLayer):
    def __init__(self, *args):
        super().__init__(*args)


if __name__ == '__main__':
    dis = MessageDisplay()
    c = ComponentLayer(message_collector=dis)
    r = Requestor(c)
    dis.activate()
    c.activate()
    r.activate()
    dis.freeze()
