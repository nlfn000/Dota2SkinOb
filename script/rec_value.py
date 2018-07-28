import json
import os
import time
from script.steammarket_api import get_value as get_steam_value
from utils.multiprocess import *
from script.dotasell_api import get_item_info as get_dotasell_value
from script.c5game_api import get_item as get_c5_price

mutex = threading.Lock()
wait_timeout = 0
ENTRY_TIME = time.strftime("%Y%m%d", time.localtime())


def for_all_items(do_func, src_site, basic_timeout=1.0):
    global mutex, wait_timeout
    name_list = []
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
    print(f'{len(lines)} recs in total,{len(lines)-len(name_list)} invalid.')
    with open('../data/item_list.dat', 'r') as f:
        for line in f.readlines():
            item = json.loads(line)
            hash_name = item['MarketHashName']
            local_name = item['LocalName']
            print(hash_name)
            if hash_name not in name_list:
                start_new_thread(do_func, (src_site, hash_name, ENTRY_TIME, local_name))
                time.sleep(basic_timeout)
                time.sleep(wait_timeout)


def rec_data(src_site, hash_name, dat_file, local_name=None):
    src_site = src_site.lower()
    if src_site == 'dotasell':
        state = get_dotasell_value(local_name)
    elif src_site == 'steammarket':
        state = get_steam_value(name=hash_name, l='english')
    elif src_site == 'c5game':
        state = get_c5_price(hash_name)
    else:
        state = None
    print(state)

    global mutex, wait_timeout

    if not state:
        if mutex.acquire():
            wait_timeout += 4
            mutex.release()
        return
    else:
        if mutex.acquire():
            wait_timeout -= 3.5
            if wait_timeout <= 0:
                wait_timeout = 0
            mutex.release()

    if mutex.acquire():
        with open('../data/' + src_site + '_data/' + dat_file + '.dat', 'a+') as f:
            state['MarketHashName'] = hash_name
            form = json.dumps(state)
            f.write(form + '\n')
        mutex.release()


if __name__ == '__main__':
    for_all_items(rec_data, src_site='dotasell', basic_timeout=0.1)
