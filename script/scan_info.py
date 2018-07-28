import json
import threading

from script.c5game_api import for_all_items
from script.dotasell_api import get_item_info

mutex = threading.Lock()
count = 0


def rec_item_names(ret):
    global mutex
    path = '../data/item_list.dat'
    name = ret.get('name')
    info = get_item_info(name)
    if info:
        if mutex.acquire():
            data = json.dumps(info)
            with open(path, 'a+') as f:
                f.write(data + '\n')
            mutex.release()


if __name__ == '__main__':
    for_all_items(rec_item_names)
