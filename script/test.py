import time

from prototypes.Layer import Layer
from prototypes.Requestor import Requestor
from utils.MessageDisplay import MessageDisplay

if __name__ == '__main__':
    dis = MessageDisplay()

    c = Layer(message_collector=dis)
    r = Requestor(c)

    dis.activate()
    c.activate()
    r.activate()

    tasks = c.input

    tasks.put({})
    time.sleep(0.5)

    c.freeze()
    r.freeze()
    dis.freeze()
