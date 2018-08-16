import requests

url = 'https://partner.steam-api.com/ISteamEconomy/GetMarketPrices/v1/?appid=570&key=0141C0F3E59100DBAECD9858C4950C49'
response = requests.get(url)
print(response)
