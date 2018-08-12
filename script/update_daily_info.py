import sys

sys.path.append('C:/Users/P51/Projects/Dota2SkinOb')

from prototypes.MessageDisplay import MessageDisplay

import json
import threading
import time

from prototypes.ProxyPool import ProxyPool
from script.update_itempool import create_if_not_exist, extract_hash, rm_repeated_records
from utils.inst_probes import *
from utils.proxies import conceal_proxies
from prototypes.Observer import Observer

ENTRY_TIME = time.strftime("%Y%m%d", time.localtime())


def _not_recorded(path):
    print(f'\033[0;33m:extracting task hash.. \033[0m')
    desc_path = '../data/item_description.json'
    _hash_d = extract_hash(desc_path, lambda d: d['hash_name'])
    _hash = extract_hash(path, lambda d: d['hash_name'])

    to_rec = [x for x in _hash_d if x not in _hash]
    print(f"\033[0;33m:{path}:{len(to_rec)} of {len(_hash_d)} not recorded. \033[0m")
    return to_rec


def _reap_daily_data(path, ob, i, full_length='?', type=1):
    for index, data in enumerate(ob.reap()):
        i = i + 1
        if type is 1:
            print(f'\033[0;34m:epoch [{i}/{full_length}]:{data}\033[0;31m')
        elif type is 2:
            print(f'\033[0;33m:epoch [{i}/{full_length}]:{data}\033[0;31m')
        with open(path, 'a+') as f:
            form = json.dumps(data)
            f.write(form + '\n')


def update_info(src_site, display_module, probe_class, enable_proxy, interval, timeout=1, type=1, ticks4reap=40,
                proxy_pool=None):
    src_site = src_site.lower()
    path = '../data/' + src_site + '_data/' + ENTRY_TIME + '.dat'
    create_if_not_exist(path)

    if not enable_proxy:
        proxy_pool = None
    ob = Observer(display_module=display_module, probe_class=probe_class, max_probes=45, proxy_pool=proxy_pool,
                  enable_proxy=enable_proxy)

    not_recorded = _not_recorded(path)
    full_length = len(not_recorded)
    count = 0

    for i, hash_name in enumerate(not_recorded):
        ob.request(hash_name=hash_name, timeout=timeout)
        time.sleep(interval)
        if ob.feedback_queue.qsize() > ticks4reap:
            _reap_daily_data(path, ob, count * ticks4reap, str(full_length), type)
            count += 1
    ob.join()
    _reap_daily_data(path, ob, count * ticks4reap, full_length=str(full_length), type=type)
    rm_repeated_records(path, keyfunc=lambda p: p['hash_name'])


if __name__ == '__main__':
    display = MessageDisplay()
    pool = ProxyPool(collect_func=conceal_proxies)
    settings = {
        'display_module': display,
        'proxy_pool': pool,
        'interval': 0.01,
        'enable_proxy': True,
        'type': 1,
        'probe_class': Probe,
        'timeout': 2,
    }
    to_update = [
        {'probe_class': DSProbe, 'src_site': 'dotasell'},
        {'probe_class': C5Probe, 'src_site': 'c5game', 'enable_proxy': True, 'type': 2},
    ]
    for site in to_update:
        t = threading.Thread(target=update_info, kwargs=dict(settings, **site))
        t.start()
