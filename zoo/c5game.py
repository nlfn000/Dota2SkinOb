from bs4 import BeautifulSoup


class C5game:
    """
        info tracker on http://www.c5game.com
    """

    url = 'https://www.c5game.com/dota.html'
    hash_key = 'k'

    @staticmethod
    def resolve_func(_h, _r):
        try:
            hash_name = _h
            soup = BeautifulSoup(_r.text, 'lxml')
            ret = {'hash_name': hash_name}
            for li in soup.find_all(attrs={'class': 'purchaseing'}):
                name = li.find('span').text.strip()
                num = li.find(attrs={'class': 'num'}).text.split(' ')[0]
                price_text = li.find(attrs={'class': 'price'}).text
                if name == hash_name:
                    ret.update(p_quantity=num, p_price=price_text)
                    break
            else:
                ret.update(p_quantity=None, p_price=None)
            for li in soup.find_all(attrs={'class': 'selling'}):
                name = li.find('span').text.strip()
                num = li.find(attrs={'class': 'num'}).text.split(' ')[0]
                price_text = li.find(attrs={'class': 'price'}).text
                if name == hash_name:
                    ret.update(s_quantity=num, s_price=price_text)
                    break
            else:
                ret.update(s_quantity=None, s_price=None)
        except Exception as e:
            print(e)
        else:
            return ret
