from utils.constants import WEI_IN_ETH
from utils.transaction.base_transaction import BaseTransaction


class NormalTransaction(BaseTransaction):
    """
    Class for processing output from get_normal_transaction_history
    """

    def __init__(self, transaction: dict) -> None:
        super().__init__(transaction)
        self.transaction_name = "normal_transaction"
        self.block_hash = transaction["blockHash"]
        self.method_id = transaction["methodId"]
        self.function_name = transaction["functionName"]
        self.cumulative_gas_used = int(transaction["cumulativeGasUsed"])
        self.gas_price = int(transaction["gasPrice"])
        self._is_error = int(transaction["isError"])
        self.nonce = int(transaction["nonce"])
        self.confirmations = int(transaction["confirmations"])
        self.transaction_index = int(transaction["transactionIndex"])
        self.tx_receipt_status = int(transaction["txreceipt_status"])

    def is_error(self) -> bool:
        return self._is_error == 1

    def value_in_eth(self):
        return self.value / WEI_IN_ETH
