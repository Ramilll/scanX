from web3 import Web3
from uniswap import Uniswap
from utils.constants import ETH_ADDRESS, ETH_DECIMALS
from utils.config import Config
from transaction_analysis.swap_transaction_result import Token

UNISWAP_FEE = 3000


def get_token_price(token: Token, token_amount) -> float:
    token_decimals = token.decimals
    token_amount = int(token_amount * 10**token_decimals)
    token_address = Web3.to_checksum_address(token.address)
    eth_address = Web3.to_checksum_address(ETH_ADDRESS)
    version = 3
    uniswap = Uniswap(
        address=None, private_key=None, version=version, provider=Config.ALCHEMY_KEY
    )
    try:
        price_out = uniswap.get_price_input(
            token_address, eth_address, token_amount, UNISWAP_FEE
        )
    except Exception as e:
        print(f"Failed to fetch price for {token}")
        return 0
    print(f"Price for {token} is {price_out / (10**ETH_DECIMALS)}")
    return price_out / (10**ETH_DECIMALS)
