from collections import defaultdict
from typing import Dict, List

from utils.etherscan_client import EtherscanClient
from utils.transaction.erc20_transaction import ERC20Transaction
from utils.transaction.internal_transaction import InternalTransaction
from utils.transaction.normal_transaction import NormalTransaction


class ProfitScanner:
    def __init__(self, address: str) -> None:
        self.etherscan_client = EtherscanClient()
        self.normal_transactions: List[NormalTransaction] = [
            NormalTransaction(tx)
            for tx in self.etherscan_client.get_normal_transaction_history(address)
        ]
        self.erc20_transactions: List[ERC20Transaction] = [
            ERC20Transaction(tx)
            for tx in self.etherscan_client.get_erc20_transaction_history(address)
        ]
        self.internal_transactions: List[InternalTransaction] = [
            InternalTransaction(tx)
            for tx in (self.etherscan_client.get_internal_transaction_history(address))
        ]

    def create_txs_by_hash(self):
        txs_by_hash = defaultdict(list)
        for tx in (
            self.normal_transactions
            + self.erc20_transactions
            + self.internal_transactions
        ):
            txs_by_hash[tx.tx_hash].append(tx)
        return txs_by_hash

    def create_function_name_by_hash(self):
        function_name_by_hash = {}
        for tx in self.normal_transactions:
            assert tx.tx_hash not in function_name_by_hash
            if tx.is_error():
                function_name_by_hash[tx.tx_hash] = "error"
            else:
                function_name_by_hash[tx.tx_hash] = tx.function_name
        return function_name_by_hash
