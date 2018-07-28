import json


def get_info(name):
    lines = None
    with open('../data/item_list.dat', 'r') as f:
        lines = f.readlines()
    for line in lines:
        data = json.loads(line)
        if data['MarketHashName'] == name or data['LocalName'] == name:
            print(data)


def remove_dup(path):
    lines = None
    ref = []
    with open(path, 'r') as f:
        lines = f.readlines()
    with open(path, 'w') as f:
        for line in lines:
            if line not in ref:
                ref.append(line)
                f.write(line)
    print(f'{len(lines)-len(ref)} dups removed.')


if __name__ == '__main__':
    # get_info('尊崇之武器套装')
    remove_dup('../data/steammarket_overall_data/20180726.dat')
