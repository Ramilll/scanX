from collections import defaultdict
from typing import Dict, List

from transaction.swap_transaction_bundle import SwapTransactionBundle
from transaction_analysis.swap_function_name import is_swap, TRANSFER
from transaction_analysis.swap_transaction_analyzer import SwapTransactionAnalyzer
from transaction_analysis.swap_transaction_result import SwapTransactionResult
from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction

from transaction_analysis.transaction_count import get_transaction_count_by_same_hash


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
        self.nor_processed_function_names = set()

    def process(self) -> List[SwapTransactionResult]:
        swap_transaction_results = []
        for tx_hash, txs in self.txs_by_hash.items():
            normal_transactions: List[NormalTransaction] = []
            erc20_transactions: List[ERC20Transaction] = []
            internal_transactions: List[InternalTransaction] = []
            for tx in txs:
                if isinstance(tx, NormalTransaction):
                    normal_transactions.append(tx)
                elif isinstance(tx, ERC20Transaction):
                    erc20_transactions.append(tx)
                elif isinstance(tx, InternalTransaction):
                    internal_transactions.append(tx)
                else:
                    raise ValueError(f"Unknown transaction type: {type(tx)}")

            if not normal_transactions:
                continue

            assert (
                len(normal_transactions) == 1
            ), "Multiple normal transactions detected"

            normal_transaction = normal_transactions[0]

            if not is_swap(normal_transaction.function_name):
                self.nor_processed_function_names.add(normal_transaction.function_name)
                continue

            assert (
                len(internal_transactions) <= 1
            ), f"Multiple internal transactions detected for {normal_transaction.function_name}, {normal_transaction.tx_hash}"

            internal_transaction = (
                internal_transactions[0] if internal_transactions else None
            )

            if normal_transaction.is_error():
                continue

            assert len(erc20_transactions) > 0, "No ERC20 transactions found for swap"

            if not SwapTransactionBundle.is_valid_count_sub_transactions(
                normal_transaction, erc20_transactions, internal_transaction
            ):
                continue

            swap_tranaction_bundle = SwapTransactionBundle(
                self.owner_address,
                normal_transaction,
                erc20_transactions,
                internal_transaction,
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

        return sorted(swap_transaction_results, key=lambda x: x.timestamp)

    def _create_txs_by_hash(self):
        txs_by_hash = defaultdict(list)
        for tx in (
            self.normal_transactions
            + self.erc20_transactions
            + self.internal_transactions
        ):
            txs_by_hash[tx.tx_hash].append(tx)
        return txs_by_hash
