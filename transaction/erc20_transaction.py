from utils.constants import WEI_IN_ETH
from transaction.base_transaction import BaseTransaction


class ERC20Transaction(BaseTransaction):
    """
    Class for processing output from get_erc20_transaction_history
    """

    def __init__(self, transaction: dict) -> None:
        super().__init__(transaction)
        self.transaction_name = "erc20_transaction"
        self.block_hash = transaction["blockHash"]
        self.token_name = transaction["tokenName"]
        self.token_symbol = transaction["tokenSymbol"]
        self.cumulative_gas_used = int(transaction["cumulativeGasUsed"])
        self.gas_price = int(transaction["gasPrice"])
        self.token_decimal = int(transaction["tokenDecimal"])
        self.nonce = int(transaction["nonce"])
        self.confirmations = int(transaction["confirmations"])
        self.transaction_index = int(transaction["transactionIndex"])

    def transaction_fee_in_wei(self):
        return self.gas_price * self.gas_used

    def transaction_fee_in_eth(self):
        return self.transaction_fee_in_wei() / WEI_IN_ETH

    def transaction_value_in_native_tokens(self):
        return self.value / (10**self.token_decimal)
