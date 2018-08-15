from forex_python.converter import CurrencyRates

from prototypes.ErrorTraceback import ErrorTraceback


class CurrencyEnhancements:
    def __init__(self, currency_type='CNY'):
        print('\033[0;36m:fetching currency rate.\033[0m')
        self.currency_type = currency_type
        self.currency_cache = CurrencyRates().get_rates(currency_type)
        self.currency_cache[currency_type] = 1.0

    def normalized_price(self, price_text):
        """
        simple currency convert toolkit

        """
        try:
            currency = {'$': 'USD',
                        'USD': 'USD',
                        '￥': 'CNY',
                        '¥': 'CNY',
                        'CNY': 'CNY'}
            price_text = price_text.replace(' ', '').replace('\'', '').replace(',', '')
            data_type = self.currency_type
            for prefix in currency:
                if prefix in price_text:
                    data_type = currency[prefix]
                price_text = price_text.replace(prefix, '')
            price = float(price_text) / self.currency_cache[data_type]
            return price
        except Exception as e:
            ErrorTraceback(e)


if __name__ == '__main__':
    ce = CurrencyEnhancements()
    a = ce.normalized_price('$123.0')
    print(a)
