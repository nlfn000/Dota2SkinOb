import json
import os
import time

from trashbin.Observer import Observer
from zoo.steam import SteamProbe


def create_if_not_exist(path):
    if not os.path.exists(path):
        with open(path, 'w'):
            pass


def rm_repeated_records(path, keyfunc=lambda d: d):
    final_lines = []
    black_list = []
    removed = 0
    with open(path, 'r') as f:
        for line in f.readlines():
            data = json.loads(line)
            key = keyfunc(data)
            if key not in black_list:
                black_list.append(key)
                final_lines.append(line)
            else:
                removed += 1
    with open(path, 'w') as f:
        for line in final_lines:
            f.write(line)
    print(f'\033[0;33m:{removed} repeated records of {removed+len(final_lines)} removed.\033[0m')


def extract_hash(path, keyfunc=lambda d: d):
    hash_list = []
    with open(path, 'r') as f:
        for line in f.readlines():
            data = json.loads(line)
            hash_list.append(keyfunc(data))
    return hash_list


def _reap_data(path, ob, i='final'):
    count = 0
    with open(path, 'a') as f:
        for feedback in ob.reap():
            for item in feedback:
                count += 1
                hash_name = item['hash_name']
                print(f'\033[0;33m:epoch {i} "{count}:{hash_name} recorded. \033[0m')
                f.write(json.dumps(item) + '\n')
    while not ob.failed_queue.empty():
        failed_task = ob.failed_queue.get()
        with open('../data/failed.tmp', 'a') as f:
            f.write(json.dumps(failed_task) + '\n')
    return count


def fetch_details(path, last_epoch=None, interval=2, size=100, epoch=302, ticks4reap=10):
    if last_epoch is None:
        with open('../data/last_epoch.tmp', 'r') as f:
            for line in f.readlines():
                last_epoch = int(line)
    ob = Observer(probe_class=SteamProbe, enable_proxy=False)
    count = 0
    for i in range(last_epoch, epoch + 1):
        start = i * size
        ob.request(start=start, target_func='detail')
        time.sleep(interval)
        if i % ticks4reap == 0:
            count += _reap_data(path, ob, str(i))
            with open('../data/last_epoch.tmp', 'w') as f:
                f.write(str(i))
    ob.join()
    _reap_data(path, ob)


def refetch_failed_task(path, interval=3):
    ob = Observer(probe_class=SteamProbe, enable_proxy=False)
    tasks = []
    with open('../data/failed.tmp', 'r') as f:
        for line in f.readlines():
            tasks.append(json.loads(line)['start'])
    with open('../data/failed.tmp', 'w') as f:
        pass
    for start in tasks:
        ob.request(start=start, target_func='detail')
        time.sleep(interval)
    ob.join()
    _reap_data(path, ob)


if __name__ == '__main__':
    fp = '../data/item_description_saver.json'
    create_if_not_exist(fp)
    fetch_details(fp)
    time.sleep(60)
    refetch_failed_task(fp)
    rm_repeated_records(fp, keyfunc=lambda p: p['hash_name'])
