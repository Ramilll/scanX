from uniswap import Uniswap

from utils.config import Config


class UniswapClient:
    def __init__(self, provider_url=Config.ALCHEMY_KEY, version=2):
        self.uniswap = Uniswap(version=version, provider=provider_url)

    def get_price_output(self, token_address_a, token_address_b, amount):
        return self.uniswap.get_price_output(token_address_a, token_address_b, amount)

    def get_price_input(self, token_address_a, token_address_b, amount):
        return self.uniswap.get_price_input(token_address_a, token_address_b, amount)

    def get_pair_reserves(self, token_address_a, token_address_b):
        return self.uniswap.get_reserves(token_address_a, token_address_b)
