import json
import os
import time

from bs4 import BeautifulSoup
from utils.basic_requests import *

# steam
base = '''http://steamcommunity.com/market/search?'''
attrs = {
    'category_570_Hero[]': 'any',
    'category_570_Slot[]': 'any',
    'category_570_Type[]': 'any',
    'appid': 570,
    'l': 'schinese',
    'q': '一艘小船'
}
requests.session().keep_alive = False


def get_value(**params):
    if 'name' in params.keys():
        params['q'] = params['name']
    for key in attrs.keys():
        if key in params.keys():
            attrs[key] = params[key]
    url = gen_url(base, attrs)
    html = get_page(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        result = soup.find(id='resultlink_0')
        if result is not None:
            name = result.find(id='result_0_name').text
            quantity = result.find(attrs={'class', 'market_listing_num_listings_qty'}).text
            price_text = result.findAll(attrs={'class', 'normal_price'})[1].text
            if name == attrs['q']:
                return {'MarketHashName': name,
                        'OnSale': quantity,
                        'Price': price_text}
    return None


def get_price_overview():
    base = 'https://steamcommunity.com/market/priceoverview/'
    attrs = {
        'currency': '1',
        'appid': 570,
        'market_hash_name': 'A Bit of Boat'
    }
    url = generate_url(attrs, base)
    html = get_page(url)
    print(url)
    print(html)


def rec_all_dota2_items(dat_file):
    name_list = []
    path = '../data/steammarket_overall_data/' + dat_file + '.dat'
    if not os.path.exists(path):
        with open(path, 'w'):
            pass
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            item = json.loads(line)
            name = item['MarketHashName']
            name_list.append(name)

    base = 'https://steamcommunity.com/market/search/render/'
    attrs = {
        'search_descriptions': '0',
        'sort_column': 'default',
        'sort_dir': 'desc',
        'appid': 570,
        'norender': 1,
        'count': 100,
        'page': 0,
    }
    url = generate_url(attrs, base)
    html = get_page(url)
    data = json.loads(html)
    total_count = data['total_count']
    page_count = int(total_count / 100)

    count = 0
    for page in range(page_count):
        try:
            count += 1
            print(count)
            if count == 25:
                time.sleep(240)
                count = 0
            time.sleep(1)
            print(f'working on page {page}')
            attrs['page'] = 0
            html = get_page(generate_url(attrs, base))
            data = json.loads(html)
            results = data['results']
            print(results[0])
            for x in results:
                if 'hash_name' not in x.keys() or x['hash_name'] in name_list:
                    continue
                x['MarketHashName'] = x['hash_name']
                x.pop('hash_name')
                x.pop('app_icon')
                x.pop('app_name')
                x.pop('asset_description')
                rec_data(path, x)
        except:
            time.sleep(60)
            page -= 1
            continue


def rec_data(path, data):
    with open(path, 'a+') as f:
        form = json.dumps(data)
        f.write(form + '\n')


def main():
    print(get_value(name='Gifts of the Vanished Isle Back', l='english'))


if __name__ == '__main__':
    # get_price_overview()
    ENTRY_TIME = time.strftime("%Y%m%d", time.localtime())
    rec_all_dota2_items(ENTRY_TIME)
