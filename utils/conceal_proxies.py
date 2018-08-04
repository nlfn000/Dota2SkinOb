import json
import time

import requests
from bs4 import BeautifulSoup

keys = ['国家', 'IP地址', '端口', '服务器地址', '是否匿名', '类型', '速度', '连接时间', '存活时间', '验证时间']


def request_proxies(pages):
    """
        keys = ['国家', 'IP地址', '端口', '服务器地址', '是否匿名', '类型', '速度', '连接时间', '存活时间', '验证时间']
    """
    base = 'http://www.xicidaili.com/nn/'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'}
    proxies = []
    for page in range(1, pages + 1):
        html = requests.get(base + str(page), headers=header).text
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find(attrs={'id': 'ip_list'})
        heads = table.find_next('tr')
        tr = heads.find_next('tr')
        while tr:
            data = parse_table(tr, 'td')
            bars = [x.get('title').replace('秒', '') for x in tr.find_all(attrs={'class': 'bar'})]
            data[6] = float(bars[0])
            data[7] = float(bars[1])
            proxies.append(data)
            tr = tr.find_next('tr')
        time.sleep(0.1)
    proxies.sort(key=lambda x: x[6], reverse=True)
    proxies = proxies[0:-int(0.3 * pages * 100)]
    proxies = [{x[5].lower(): x[1] + ":" + x[2]} for x in proxies]
    return proxies


def get_proxies(proxy_oversea=False, pages=5):
    if proxy_oversea:
        print('break jail!')
    with open('../data/proxies/proxies.dat', 'r') as f:
        lines = f.readlines()
    last_update = time.struct_time(json.loads(lines[0]))
    now = time.localtime()
    delta = time.mktime(now) - time.mktime(last_update)
    if delta > 16 * 60:
        data = request_proxies(pages)
        print(f'\033[0;36m:{len(data)} new proxies fetched.\033[0m')
        last_update = now
    else:
        lines.pop(0)
        data = [json.loads(line) for line in lines]
    with open('../data/proxies/proxies.dat', 'w') as f:
        f.write(json.dumps(last_update) + '\n')
        for d in data:
            f.write(json.dumps(d) + '\n')
    return data


def parse_table(tr, tag):
    return [th.text for th in tr.find_all(tag)]


if __name__ == '__main__':
    print(get_proxies())
