import json
import os
import sys
import threading
import time

from script.update_itempool import create_if_not_exist, extract_hash, rm_repeated_records
from utils.inst_probes import *

sys.path.append('C:/Users/P51/Dota2SkinOb')

from prototypes.Observer import Observer

ENTRY_TIME = time.strftime("%Y%m%d", time.localtime())


def _not_recorded(path):
    print(f'\033[0;33m:extracting task hash.. \033[0m')
    desc_path = '../data/item_description.json'
    _hash_d = extract_hash(desc_path, lambda d: d['hash_name'])
    _hash = extract_hash(path, lambda d: d['hash_name'])

    to_rec = [x for x in _hash_d if x not in _hash]
    print(f'\033[0;33m:{len(to_rec)} of {len(_hash_d)} not recorded. \033[0m')
    return to_rec


def _reap_daily_data(path, ob, i='final', type=1):
    for data in ob.reap():
        if type is 1:
            print(f'\033[0;34m:epoch {i}:{data}\033[0;31m')
        elif type is 2:
            print(f'\033[0;33m:epoch {i}:{data}\033[0;31m')
        with open(path, 'a+') as f:
            form = json.dumps(data)
            f.write(form + '\n')


def update_info(src_site, ticks4reap=10):
    src_site = src_site.lower()
    path = '../data/' + src_site + '_data/' + ENTRY_TIME + '.dat'
    create_if_not_exist(path)

    if src_site == 'dotasell':
        ProbeType = DSProbe
        interval = 0.05
        enable_proxy = True
        type = 1
    elif src_site.lower() == 'c5game':
        ProbeType = C5Probe
        interval = 0.04
        enable_proxy = False
        type = 2
    else:
        return

    ob = Observer(ProbeType, enable_proxy=enable_proxy)
    for i, hash_name in enumerate(_not_recorded(path)):
        ob.request(hash_name=hash_name)
        time.sleep(interval)
        if i % ticks4reap == 0:
            _reap_daily_data(path, ob, str(i), type)
    ob.join()
    _reap_daily_data(path, ob, type=type)
    rm_repeated_records(path, keyfunc=lambda p: p['hash_name'])


if __name__ == '__main__':
    t = threading.Thread(target=update_info, kwargs={'src_site': 'c5game'})
    t.start()
    t = threading.Thread(target=update_info, kwargs={'src_site': 'dotasell'})
    t.start()
