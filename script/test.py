from trashbin.ProbeCluster import ProbeCluster
from prototypes.ProxyPool import ProxyPool
from utils.LogDisplay import LogDisplay
from zoo.c5game import C5gameProbe

if __name__ == '__main__':
    dis = LogDisplay()

    proxies = ProxyPool()
    p = ProbeCluster(message_collector=dis, probe_type=C5gameProbe, proxy_pool=proxies)
    # p = C5gameProbe(message_collector=dis, proxy_pool=proxies)
    # p = C5gameProbe(message_collector=dis)

    dis.activate()
    proxies.activate()
    p.activate()

    tasks = p.input

    tasks.put(dict(hash_name='Astral Drift'))
    tasks.put(dict(hash_name='Astral Drift'))
    tasks.put(dict(hash_name='Astral Drift'))
    tasks.put(dict(hash_name='Astral Drift'))
    tasks.put(dict(hash_name='Astral Drift'))
    tasks.put(dict(hash_name='Astral Drift'))

    print(p.output.get())
    print(p.output.get())
    print(p.output.get())
    print(p.output.get())
    print(p.output.get())
    print(p.output.get())

    p.freeze()
    dis.freeze()
    proxies.freeze()
