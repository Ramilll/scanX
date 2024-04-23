import requests

def get_token_price(token_address) -> float:
        url = f'https://api.geckoterminal.com/api/v2/simple/networks/eth/token_price/{token_address.lower()}'
        parameters = {'accept': 'application/json'}
        response = requests.get(url, headers=parameters)
        if response.status_code == 200:
                data = response.json()
                try:
                        token_price = float(data['data']['attributes']['token_prices'][token_address.lower()])
                        return token_price
                except Exception as ex:
                        return None
        else:
                return None
