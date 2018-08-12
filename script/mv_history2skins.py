import json

path_history = '../data/item_history.json'
base = '../data/skins/'
with open(path_history, 'r') as f:
    lines = f.readlines()
for line in lines:
    data = json.loads(line)
    print(data)
    hash_name = data['hash_name']
    data = data['data']
    with open(base + hash_name + '.sth', 'w') as f:
        if data['success']:
            for day in data['prices']:
                f.write(json.dumps(day) + '\n')
