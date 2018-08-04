import json
import os
import time

from prototypes.Observer import Observer
from prototypes.Probe import SteamProbe


def all_items():
    ret = []
    with open('../data/item_list.dat', 'r') as f:
        for line in f.readlines():
            item = json.loads(line)
            hash_name = item['MarketHashName']
            ret.append(hash_name)
    return ret


def create_if_not_exist(path):
    if not os.path.exists(path):
        with open(path, 'w'):
            pass


def remove_dup(path):
    data = []
    name_list = []
    count = 0
    with open(path, 'r') as f:
        for line in f.readlines():
            count += 1
            item = json.loads(line)
            hash_name = item['MarketHashName']
            if hash_name not in name_list:
                data.append(line)
                name_list.append(hash_name)
        print(f':{count-len(name_list)} dup records removed')

    with open(path, 'w') as f:
        for line in data:
            f.write(line)


def rest_of_items(path):
    item_list = all_items()
    total_length = len(item_list)
    create_if_not_exist(path)
    remove_dup(path)
    with open(path, 'r') as f:
        for line in f.readlines():
            item = json.loads(line)
            hash_name = item['MarketHashName']
            while hash_name in item_list:
                item_list.remove(hash_name)
    print(f':{total_length} recs in total,{len(item_list)} uncaught.')
    return item_list


def get_timeout(total_hours=4):
    timeout = total_hours * 60 * 60 / 10000
    return timeout


def rec_steam_data():
    session_id = '74e1e50281794c2992253bde'
    steam_login_secure = '76561198123694279||983226F68D779659EA12223C7311E3AD4EFE6CA9'
    ENTRY_TIME = time.strftime("%Y%m%d", time.localtime())
    path = '../data/steam_history_data/' + str(ENTRY_TIME) + '.dat'
    ob = Observer(SteamProbe, session_id=session_id, steam_login_secure=steam_login_secure)

    batch = 0
    for item in rest_of_items(path):
        ob.request(item, timeout=30, type='history')
        time.sleep(get_timeout())
    ob.task_queue.join()
    with open(path, 'a') as f:
        for x in ob.reap():
            print(f'\033[0;33m batch {batch}"{x}\033[0m')
            f.write(json.dumps(x) + '\n')
    ob.sleep()
    time.sleep(10)
    print('all done')


if __name__ == '__main__':
    # rec_steam_data() # dont use this again!
    remove_dup('../data/c5game_data/20180805.dat')
