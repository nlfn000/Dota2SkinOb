import json
import threading
import time

from prototypes.Observer import Observer
from zoo.steam import SteamProbe

stop_fetch_data = threading.Lock()


def rm_repeated_records(path):
    final_lines = []
    black_list = []
    total = 0
    count = 0
    with open(path, 'r') as f:
        for line in f.readlines():
            data = json.loads(line)
            total += 1
            key = data['hash_name']
            if data.get('item_nameid'):
                if key not in black_list:
                    count += 1
                    black_list.append(key)
                    final_lines.append(line)
    print(f'------------{len(final_lines)}')
    with open(path, 'r') as f:
        for line in f.readlines():
            data = json.loads(line)
            key = data['hash_name']
            if key not in black_list:
                black_list.append(key)
                final_lines.append(line)

    with open(path, 'w') as f:
        for line in final_lines:
            f.write(line)
    print(f'\033[0;33m:{total-len(final_lines)} repeated records of {len(final_lines)} removed.\033[0m')


def _reap(ob, data, path):
    while not stop_fetch_data.locked():
        for x in ob.reap():
            for d in data:
                if d['hash_name'] == x['hash_name']:
                    d.update(x)
                    with open(path, 'a') as f:
                        f.write(json.dumps(d) + '\n')
                    print(d)
                    break
        time.sleep(15)


def fetch_data(path):
    data = []
    with open(path, 'r') as f:
        for line in f.readlines():
            d = json.loads(line)
            if not d.get('item_nameid'):
                data.append(d)

    ob = Observer(probe_class=SteamProbe, enable_proxy=False, max_probes=5)

    t = threading.Thread(target=_reap, kwargs={'ob': ob, 'data': data, 'path': path})
    t.start()

    for d in data:
        hash_name = d['hash_name']
        ob.request(hash_name=hash_name, target_func='nameid')
        time.sleep(1)

    ob.join()
    stop_fetch_data.acquire()


if __name__ == '__main__':
    fp = '../data/item_description.json'
    rm_repeated_records(fp)
    fetch_data(fp)
