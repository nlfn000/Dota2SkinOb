import json
import os
import sys
import threading
import time

sys.path.append('C:/Users/P51/Dota2SkinOb')

from prototypes.Observer import Observer
from prototypes.Probe import DSProbe, C5Probe

ENTRY_TIME = time.strftime("%Y%m%d", time.localtime())
name_list = []

mutex = threading.Lock()


def check_path(src_site):
    global name_list
    path = '../data/' + src_site + '_data/' + ENTRY_TIME + '.dat'
    if not os.path.exists(path):
        with open(path, 'w'):
            pass
    with open(path, 'r') as f:
        lines = f.readlines()
    with open(path, 'w') as f:
        for line in lines:
            item = json.loads(line)
            name = item['MarketHashName']
            price = item['Price']
            if price:
                name_list.append(name)
                f.write(line)
    print(f'{len(lines)} records exists,{len(lines)-len(name_list)} invalid.')
    return len(lines)


def all_items():
    global name_list
    ret = []
    with open('../data/item_list.dat', 'r') as f:
        for line in f.readlines():
            item = json.loads(line)
            hash_name = item['MarketHashName']
            if hash_name not in name_list:
                ret.append(hash_name)
    return ret


def rec_data(src_site):
    total = len(all_items()) - check_path(src_site)
    print(f'{total} items to fetch.')
    if src_site.lower() == 'dotasell':
        ProbeType = DSProbe
        timeout = 0.05
        disable_proxy = False
    elif src_site.lower() == 'c5game':
        ProbeType = C5Probe
        timeout = 0.1
        disable_proxy = False
    else:
        return

    ob = Observer(ProbeType, disable_proxy=disable_proxy, max_retry=5)
    count = 0
    rec = 0
    for item in all_items():
        ob.request(item, shuffle_proxies=False)
        time.sleep(timeout)
        if count % 10 == 0:
            for data in ob.reap():
                rec += 1
                print(f'\033[0;32m:[{rec}/{total}]:{data}\033[0;31m')
                if mutex.acquire():
                    with open('../data/' + src_site + '_data/' + ENTRY_TIME + '.dat', 'a+') as f:
                        form = json.dumps(data)
                        f.write(form + '\n')
                    mutex.release()
    ob.task_queue.join()
    ob.sleep()
    time.sleep(10)
    for data in ob.reap():
        rec += 1
        print(f'\033[0;32m:[{rec}/{total}]:{data}\033[0;31m')
        if mutex.acquire():
            with open('../data/' + src_site + '_data/' + ENTRY_TIME + '.dat', 'a+') as f:
                form = json.dumps(data)
                f.write(form + '\n')
            mutex.release()


if __name__ == '__main__':
    # rec_data(src_site=sys.argv[1])
    rec_data(src_site='c5game')
