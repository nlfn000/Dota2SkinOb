import json

from utils.basic_requests import *

requests.session().keep_alive = False
base = 'http://www.dotasell.com/xhr/json_search.ashx'


def do_nothing(param):
    pass


def get_sales_info(hash_name):
    base_sales = 'http://www.dotasell.com/xhr/json_ItemsInSale.ashx?appid=570'
    req_data = {
        'GemNeedle': ['-1'],
        'HashName': hash_name,
        'onlytradable': 'True',
        'start': '0',
        'StyleNeedle': '-1'
    }
    response = requests.post(base_sales, json=req_data)
    if response:
        data = json.loads(response.text)
        sale_info = data.get('SaleInfo')
        return [x['PriceCNYString'] for x in sale_info]


def get_item_info(item_name):
    req_data = {
        'appid': '570',
        'keyw': item_name,
        'Sockets': '0',
        'start': '0',
        'fuzz': 'true',
        'AssetsType': '0',
        'OrderBy': 'Default',
        'safeonly': 'false'
    }
    response = get_response(generate_url(req_data, base))
    if response:
        data = response.json()
        if data and 'MerchandiseList' in data:
            items = data.get('MerchandiseList')
            for item in items:
                name = item.get('LocalName')
                hash_name = item.get('MarketHashName')
                info = get_sales_info(hash_name)
                if name.replace(' ', '') == item_name.replace(' ', ''):
                    return {
                        'Price': item['LocalPrice'],
                        'SaleInfo': info
                    }
    else:
        print(response)


def for_all_items(do_function=do_nothing):
    req_data = {
        'Sockets': '0',
        'start': '0',
        'AssetsType': '0',
        'OrderBy': 'Default',
        'AppID': '570',
        'safeonly': 'false'
    }
    start = 0
    while True:
        req_data['start'] = str(start)
        start = start + 80
        url = generate_url(req_data, base)
        response = get_response(url)
        if response:
            data = response.json()
            if data and 'MerchandiseList' in data:
                items = data.get('MerchandiseList')
                if len(items) < 1:
                    break
                for item in items:
                    do_function(item)
                continue
        break


def main():
    # for_all_items(do something here)
    print(get_item_info('嘲讽：仰泳！'))
    # pass


if __name__ == '__main__':
    main()
