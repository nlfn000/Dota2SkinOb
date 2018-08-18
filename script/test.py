import time

from prototypes.ComponentLayer import ComponentLayer
from prototypes.Requestor import Requestor
from utils.MessageDisplay import MessageDisplay

if __name__ == '__main__':
    dis = MessageDisplay()

    c = ComponentLayer(message_collector=dis)
    r = Requestor(input_layer=c)
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
