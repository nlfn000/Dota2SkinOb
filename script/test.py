import json
import threading
import time

from prototypes.Currency import CurrencyEnhancements
from prototypes.Observer import Observer
from utils.probe_zoo import SteamProbe

data = []
with open('../data/item_description.json', 'r') as f:
    for line in f.readlines():
        d = json.loads(line)
        if not d.get('item_nameid'):
            data.append(d)

ob = Observer(probe_class=SteamProbe, enable_proxy=False, max_probes=10)
ob.log.settings(quest_message=True)

for d in data:
    hash_name = d['hash_name']
    ob.request(hash_name=hash_name, target_func='nameid')


def reap(ob):
    while not ob.task_queue.empty():
        for x in ob.reap():
            for d in data:
                if d['hash_name'] == x['hash_name']:
                    d.update(x)
                    print(d)
                    break
        with open('../data/item_description.json', 'w') as f:
            for d in data:
                f.write(json.dumps(d) + '\n')
        time.sleep(4)


t = threading.Thread(target=reap, kwargs={'ob': ob})
t.start()

ob.join()
