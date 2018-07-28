import time

from bs4 import BeautifulSoup
from utils.basic_requests import *
from utils.basic_bs4 import *
from utils.multiprocess import *

ENTRY_TIME = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())


def do_nothing(*params):
    return params


def get_user_info(cookie):
    print('Scanning user info on c5...')
    username = None
    balance = None

    # get username&balance
    header = {
        'User-Agent': '''Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 
        Safari/537.36''',
        'Connection': 'keep-alive',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cookie': cookie
    }
    url = 'https://www.c5game.com/user.html'
    html = get_page(url, header)
    if html:
        user_page = BeautifulSoup(html, 'lxml')
        username = find_by_class(user_page, 'name name-ellipsis ft-16').text
        balance = find_by_class(user_page, 'ft-orange ft-28').text
    time_stamp = int(time.mktime(time.localtime()))
    info = {'time_stamp': time_stamp, 'username': username, 'account_balance': balance}

    # get info in json
    url = 'https://www.c5game.com/api/user/bill.html'
    json = get_response(url, header).json()
    if json:
        info.update(json.get('body'))
    return info


def get_favorite(cookie):
    homepage = "https://www.c5game.com"
    url = "https://www.c5game.com/user/favorite/index.html"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/53.0.2785.143 Safari/537.36',
        'Connection': 'keep-alive',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cookie': cookie
    }
    htmls = [get_page(url, header)]
    soup = BeautifulSoup(htmls[0], 'lxml')
    yw1 = soup.find(id='yw1')
    if yw1:
        hrefs = find_all_by_class(yw1, 'page')
        for href in hrefs:
            url = homepage + href.find('a').get('href')
            htmls.append(get_page(url, header))

    items = []
    for html in htmls:
        soup = BeautifulSoup(html, 'lxml')
        trs = soup.find(id='yw0').findAll('tr')
        items.extend([tr.find('img').get('alt') for tr in trs])
    return items


def for_item(item_name, do_function=do_nothing):
    url = 'https://www.c5game.com/dota.html?locale=zh&k=' + item_name
    return scan_page_deprecated(url, do_function)


def urls_of_all_heros():
    html = get_page("https://www.c5game.com/dota.html?locale=zh")
    if html:
        soup = BeautifulSoup(html, 'lxml')
        return [filter_hero.find('a').get('href') for filter_hero in find_all_by_class(soup, 'filter-hero')]


def for_all_items(do_function=do_nothing, use_multi_process=True):
    urls = urls_of_all_heros()
    urls.extend([
        'https://www.c5game.com/dota.html?type=socket_gem&page=1',
        'https://www.c5game.com/dota.html?type=emoticon_tool&page=1',
        'https://www.c5game.com/dota.html?type=announcer&page=1',
        'https://www.c5game.com/dota.html?type=tool&page=1',
        'https://www.c5game.com/dota.html?type=retired_treasure_chest&page=1',
        'https://www.c5game.com/dota.html?type=pennant&page=1',
        'https://www.c5game.com/dota.html?type=courier&page=1',
        'https://www.c5game.com/dota.html?type=music&page=1',
        'https://www.c5game.com/dota.html?type=hud_skin&page=1',
        'https://www.c5game.com/dota.html?type=misc&page=1',
        'https://www.c5game.com/dota.html?type=loading_screen&page=1',
        'https://www.c5game.com/dota.html?type=treasure_chest&page=1',
        'https://www.c5game.com/dota.html?type=cursor_pack&page=1',
        'https://www.c5game.com/dota.html?type=ward&page=1'
    ])
    params = [(url, do_function) for url in urls]
    for param in params:
        if use_multi_process:
            start_new_thread(scan_url, param)
        else:
            scan_url(*param)


def scan_url(url, do_function):
    print(f'scanning {url}')
    html = get_page(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        last_page = find_by_class(soup, 'last')
        if last_page:
            split = last_page.find('a').get('href').split('page=')
            if len(split) > 1:
                max_page = int(split[1])
            else:
                max_page = 1
            base = url.split('page=')[0] + 'page='
            for x in range(1, max_page + 1):
                url = base + str(x)
                scan_page_deprecated(url, do_function)


def scan_page_deprecated(url, do_function=do_nothing):
    html = get_page(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        base = 'https://www.c5game.com'
        for li in find_all_by_class(soup, 'selling'):
            scan_item_deprecated(
                url=base + li.find('a').get('href') + '?locale=zh',
                do_function=do_function,
                price=find_by_class(li, 'price').text,
            )
        for li in find_all_by_class(soup, 'purchaseing'):
            scan_item_deprecated(
                url=base + li.find('a').get('href') + '?locale=zh',
                do_function=do_function,
                price=find_by_class(li, 'price').text,
                purchasing=True
            )


def scan_item_deprecated(url, do_function=do_nothing, price=None, purchasing=False):
    html = get_page(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        name = find_by_class(soup, 'name').find('span').text
        info = find_by_class(soup, 'sale-item-info')
        details = [c for c in find_by_class(info, 'ft-gray mt-5').children]
        quality = details[-6].text
        rarity = details[-4].text
        type = details[-2].text
        ret = {
            'name': name,
            'quality': quality,
            'rarity': rarity,
            'type': type,
            'price': price,
            'purchasing': purchasing
        }
        do_function(ret)


def update_c5_db(ret):
    form = {
        'name': ret.get('name'),
        'price': ret.get('price'),
        'purchasing': ret.get('purchasing')
    }
    print(form)
    # save_to_mongo(form, db=mongo_db, table_name='c5_2017_10_24')


def main():
    # a sample usage
    # change the func below with anything you want
    for_all_items(update_c5_db)


# new api------------------------------------------------------


def get_item(hash_name):
    base = 'https://www.c5game.com/dota.html?min=&max=&k='
    html = get_page(base + str(hash_name))
    if html:
        soup = BeautifulSoup(html, 'lxml')
        for li in find_all_by_class(soup, 'selling'):
            name = li.find('span').text
            num = li.find(attrs={'class': 'num'}).text.split(' ')[0]
            price_text = find_by_class(li, 'price').text
            if name == hash_name:
                return {'MarketHashName': hash_name,
                        'OnSale': num,
                        'Price': price_text}
    return None


if __name__ == '__main__':
    # main()
    p = get_item('Inscribed Golden Moonfall')
    print(p)