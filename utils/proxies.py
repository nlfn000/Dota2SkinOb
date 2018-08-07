import json
import time

import requests
from bs4 import BeautifulSoup

keys = ['国家', 'IP地址', '端口', '服务器地址', '是否匿名', '类型', '速度', '连接时间', '存活时间', '验证时间']


def _parse_table(tr, tag):
    return [th.text for th in tr.find_all(tag)]


def request_proxies(pages, rate=0.3):
    """
        keys = ['国家', 'IP地址', '端口', '服务器地址', '是否匿名', '类型', '速度', '连接时间', '存活时间', '验证时间']
    """
    base = 'http://www.xicidaili.com/nn/'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 '
                      'Safari/537.36'}
    proxies = []
    for page in range(1, pages + 1):
        html = requests.get(base + str(page), headers=header).text
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find(attrs={'id': 'ip_list'})
        heads = table.find_next('tr')
        tr = heads.find_next('tr')
        while tr:
            data = _parse_table(tr, 'td')
            bars = [x.get('title').replace('秒', '') for x in tr.find_all(attrs={'class': 'bar'})]
            data[6] = float(bars[0])
            data[7] = float(bars[1])
            proxies.append(data)
            tr = tr.find_next('tr')
        time.sleep(0.1)
    proxies.sort(key=lambda x: x[6], reverse=True)
    proxies = proxies[0:-int(rate * pages * 100)]
    proxies = [{x[5].lower(): x[1] + ":" + x[2]} for x in proxies]
    return proxies


def conceal_proxies(pages=5, rate=0.3, **kwargs):
    json_data = []
    with open('../data/proxies/proxies.dat', 'r') as f:
        for line in f.readlines():
            json_data.append(json.loads(line))
    last_update = time.struct_time(json_data[0])
    now = time.localtime()
    delta = time.mktime(now) - time.mktime(last_update)
    if delta > 16 * 60:
        last_update = now
        json_data = [last_update]
        data = request_proxies(pages, rate)
        json_data.extend(data)
        print(f'\033[0;36m:{len(data)} new proxies fetched.\033[0m')
        with open('../data/proxies/proxies.dat', 'w') as f:
            for d in json_data:
                f.write(json.dumps(d) + '\n')
    else:
        print(f'\033[0;36m:{len(json_data)-1} proxies loaded.- '
              f'last update:{time.strftime("%Y.%m.%d-%H:%M",last_update)}\033[0m')
    json_data.pop(0)
    return json_data


if __name__ == '__main__':
    print(conceal_proxies())
