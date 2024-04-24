from web3 import Web3
from uniswap import Uniswap

def get_token_price(token_address, token_decimals, token_amount) -> float:

    eth_address = Web3.to_checksum_address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
    eth_decimals = 18

    ALCHEMY_KEY = 'https://eth-mainnet.g.alchemy.com/v2/939THemxLlThMsjblHUIWl89plPtayML'


    token_amount = int(token_amount * 10 ** token_decimals)
    token_address = Web3.to_checksum_address(token_address)
    version = 3
    uniswap = Uniswap(address=None, private_key=None, version=version, provider=ALCHEMY_KEY)
    price_out = uniswap.get_price_input(token_address, eth_address, token_amount)
    return price_out / (10 ** eth_decimals)