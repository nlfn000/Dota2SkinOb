import time

from prototypes.Layer import Layer
from prototypes.ProxyPool import ProxyPool
from prototypes.Requestor import Requestor
from utils.MessageDisplay import MessageDisplay
from zoo.c5game import C5gameProbe

if __name__ == '__main__':
    dis = MessageDisplay()

    proxies = ProxyPool()
    p = C5gameProbe(message_collector=dis, proxy_pool=proxies)
    # p = C5gameProbe(message_collector=dis)

    dis.activate()
    proxies.activate()
    p.activate()

    tasks = p.input

    tasks.put(dict(hash_name='Astral Drift'))
    print(p.output.get())

    p.freeze()
    dis.freeze()
    proxies.freeze()
