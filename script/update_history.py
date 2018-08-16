import json
import time

from prototypes.Observer import Observer
from script.update_itempool import extract_hash, create_if_not_exist, rm_repeated_records
from private.login_settings import *
from zoo.steam import SteamProbe


def _not_recorded():
    print(f'\033[0;33m:extracting task hash.. \033[0m')
    desc_path = '../data/item_description.json'
    hash_d = extract_hash(desc_path, lambda d: d['hash_name'])

    hist_path = '../data/item_history.json'
    hash_h = extract_hash(hist_path, lambda d: d['hash_name'])

    to_rec = [x for x in hash_d if x not in hash_h]
    print(f'\033[0;33m:{len(to_rec)} of {len(hash_d)} not recorded. \033[0m')
    return to_rec


def _reap_history_data(path, ob, i='final'):
    with open(path, 'a') as f:
        for feedback in ob.reap():
            hash_name = feedback['hash_name']
            print(f'\033[0;33m:epoch {i} ":{hash_name} recorded. \033[0m')
            f.write(json.dumps(feedback) + '\n')


def _transfer_old_data(from_path, to_path):
    final_lines = []
    with open(from_path, 'r') as f:
        for line in f.readlines():
            data = json.loads(line)
            if 'MarketHashName' in data:
                data['hash_name'] = data.pop('MarketHashName')
            final_lines.append(json.dumps(data))
    with open(to_path, 'a') as f:
        for line in final_lines:
            f.write(line + '\n')


def fetch_history(path, not_recorded, interval=0.6, ticks4reap=5):
    ob = Observer(probe_class=SteamProbe, enable_proxy=False)
    ob.auth(steamLoginSecure=steamLoginSecure, sessionid=sessionid)

    for i, item in enumerate(not_recorded):
        ob.request(hash_name=item, target_func='history', timeout=15)
        time.sleep(interval)
        if i % ticks4reap == 0:
            _reap_history_data(path, ob, str(i))
    ob.join()
    _reap_history_data(path, ob)


fp = '../data/item_history.json'
create_if_not_exist(fp)
# _transfer_old_data('../data/steam_history_data/20180804.dat', fp)
fetch_history(fp, _not_recorded())
rm_repeated_records(fp, keyfunc=lambda p: p['hash_name'])
