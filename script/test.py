import time

from prototypes.ComponentLayer import ComponentLayer
from prototypes.Requestor import Requestor
from utils.MessageDisplay import MessageDisplay

if __name__ == '__main__':
    dis = MessageDisplay()

    c = ComponentLayer(message_collector=dis)
    r = Requestor(input_layer=c, url='http://www.baidu.com')

    dis.activate()
    c.activate()
    r.activate()

    tasks = c.input

    tasks.put({})
    time.sleep(0.5)

    c.freeze()
    r.freeze()
    dis.freeze()
