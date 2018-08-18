from bs4 import BeautifulSoup

from models.Probe import Probe
from prototypes.Requestor import Requestor
from prototypes.Resolver import Resolver
from utils.ErrorReceiver import handle_error


class C5gameProbe(Probe):
    """
        info tracker on http://www.c5game.com
    """

    class InnerRequestor(Requestor):
        def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id='', **kwargs):
            super().__init__(input_layer, input, output, message_collector, id, **kwargs)
            self.set(url='https://www.c5game.com/dota.html')

        def request(self, **keys):
            keys['k'] = keys['hash_name']
            keys.pop('hash_name')
            return super().request(**keys)

    class InnerResolver(Resolver):

        def _service(self):
            while True:
                keys, response = self.input.get()
                try:
                    hash_name = keys.get('hash_name')
                    soup = BeautifulSoup(response.text, 'lxml')
                    ret = {hash_name: 'hash_name'}
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
                    handle_error(e)
                else:
                    self.output.put(ret)

    def __init__(self, input_layer=None, input=None, output=None, message_collector=None, id=''):
        super().__init__(input_layer, input, output, message_collector, id)

        requestor = self.InnerRequestor(input=self.input, message_collector=self.message, id=id)  # build the net
        resolver = self.InnerResolver(requestor, output=self.output, id=id)

        self.requestor = requestor
        self.resolver = resolver
        layers = [requestor, resolver]
        self.layers = layers
