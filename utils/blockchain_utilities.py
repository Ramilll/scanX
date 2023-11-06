from web3 import Web3

from utils.config import Config
from utils.constants import WEI_IN_ETH


class BlockchainUtilities:
    def __init__(self, provider_url=Config.ALCHEMY_KEY):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))

    def is_connected(self):
        return self.web3.isConnected()

    def get_latest_block_number(self):
        return self.web3.eth.block_number

    def get_block_by_number(self, block_number):
        return self.web3.eth.get_block(block_number)

    def to_checksum_address(self, address):
        return self.web3.to_checksum_address(address)

    def get_wei_balance(self, address, block_number=None):
        address = self.to_checksum_address(address)
        return self.web3.eth.get_balance(address, block_identifier=block_number)

    def get_eth_balance(self, address, block_number=None):
        return self.get_wei_balance(address, block_number) / WEI_IN_ETH

    def get_code(self, address):
        address = self.to_checksum_address(address)
        return self.web3.eth.get_code(address)

    def get_transaction_receipt(self, tx_hash):
        return self.web3.eth.get_transaction_receipt(tx_hash)

    def get_transaction(self, tx_hash):
        return self.web3.eth.get_transaction(tx_hash)
