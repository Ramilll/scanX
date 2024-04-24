from collections import defaultdict
from typing import Dict, List

from transaction.swap_transaction_bundle import SwapTransactionBundle
from transaction_analysis.swap_function_name import is_swap
from transaction_analysis.swap_transaction_analyzer import SwapTransactionAnalyzer
from transaction_analysis.swap_transaction_result import SwapTransactionResult
from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction


class ProfitScanner:
    SWAP_TRANSACTION_ANALYZER = SwapTransactionAnalyzer

    def __init__(
        self,
        owner_address: str,
        normal_transactions: List[NormalTransaction],
        erc20_transactions: List[ERC20Transaction],
        internal_transactions: List[InternalTransaction],
    ) -> None:
        self.owner_address = owner_address
        self.normal_transactions = normal_transactions
        self.erc20_transactions = erc20_transactions
        self.internal_transactions = internal_transactions

        self.txs_by_hash = self._create_txs_by_hash()

    def process(self) -> List[SwapTransactionResult]:
        swap_transaction_results = []
        for tx_hash, txs in self.txs_by_hash.items():
            normal_transactions: List[NormalTransaction] = []
            erc20_transactions: List[ERC20Transaction] = []
            internal_transaction: List[InternalTransaction] = []
            for tx in txs:
                if isinstance(tx, NormalTransaction):
                    normal_transactions.append(tx)
                elif isinstance(tx, ERC20Transaction):
                    erc20_transactions.append(tx)
                elif isinstance(tx, InternalTransaction):
                    internal_transaction.append(tx)
                else:
                    raise ValueError(f"Unknown transaction type: {type(tx)}")

            if not normal_transactions or not is_swap(
                normal_transactions[0].function_name
            ):
                continue

            assert (
                len(normal_transactions) == 1
            ), "Multiple normal transactions detected"

            assert (
                len(internal_transaction) <= 1
            ), "Multiple internal transactions detected"

            normal_transaction = normal_transactions[0]

            if normal_transaction.is_error():
                continue

            if len(erc20_transactions) == 0:
                print(f"No ERC20 transactions found for swap: {tx_hash}")
                continue

            swap_tranaction_bundle = SwapTransactionBundle(
                self.owner_address,
                normal_transaction,
                erc20_transactions,
                internal_transaction[0] if internal_transaction else None,
            )

            if not swap_tranaction_bundle.is_valid():
                print(f"Invalid swap transaction: {tx_hash}")
                continue

            swap_transaction_result = (
                SwapTransactionAnalyzer.get_swap_transaction_result(
                    swap_tranaction_bundle
                )
            )
            swap_transaction_results.append(swap_transaction_result)

        return swap_transaction_results

    def _create_txs_by_hash(self):
        txs_by_hash = defaultdict(list)
        for tx in (
            self.normal_transactions
            + self.erc20_transactions
            + self.internal_transactions
        ):
            txs_by_hash[tx.tx_hash].append(tx)
        return txs_by_hash
