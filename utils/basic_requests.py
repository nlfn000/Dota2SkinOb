from urllib.parse import urlencode

import requests


def get_response(url, header=None, proxies=None, timeout=300):
    try:
        url = url.encode('utf-8')
        with requests.get(url, headers=header, proxies=proxies, timeout=timeout) as response:
            return response
    except TimeoutError:
        print(f'timeout_getting_response: url={url}')


def get_page(url, header=None, proxies=None):
    response = get_response(url, header=header, proxies=proxies)
    if response and response.status_code == 200:
        return response.text
    else:
        print(response)


def gen_url(base, attrs):
    st = False
    for key in attrs.keys():
        if st:
            st = True
        else:
            base += '&'
        base += key + '=' + str(attrs[key])
    return base


def generate_url(req_data, base):
    params = urlencode(req_data)
    return base + '?' + params
