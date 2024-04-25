from collections import defaultdict
from typing import Dict, List, Union
from dataclasses import asdict, dataclass, field

from transaction.swap_transaction_bundle import SwapTransactionBundle
from transaction_analysis.swap_function_name import is_swap, TRANSFER
from transaction_analysis.swap_transaction_analyzer import SwapTransactionAnalyzer
from transaction_analysis.swap_transaction_result import SwapTransactionResult
from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction


@dataclass
class SkippedTransactionReasons:
    no_normal_transaction: int = 0
    error: int = 0
    not_valid_count_sub_transactions: int = 0
    not_valid_bundle: int = 0
    not_swap_transaction: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def to_dict(self) -> dict:
        # Manually construct the dictionary to ensure proper serialization
        return {
            "no_normal_transaction": self.no_normal_transaction,
            "error": self.error,
            "not_valid_count_sub_transactions": self.not_valid_count_sub_transactions,
            "not_valid_bundle": self.not_valid_bundle,
            "not_swap_transaction": dict(
                self.not_swap_transaction
            ),  # Convert defaultdict to dict explicitly
        }


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

    def process(self) -> Union[List[SwapTransactionResult], SkippedTransactionReasons]:
        swap_transaction_results = []
        skip_transaction_reasons = SkippedTransactionReasons()
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
                skip_transaction_reasons.no_normal_transaction += 1
                continue

            assert (
                len(normal_transactions) == 1
            ), "Multiple normal transactions detected"

            normal_transaction = normal_transactions[0]

            if not is_swap(normal_transaction.function_name):
                skip_transaction_reasons.not_swap_transaction[
                    normal_transaction.function_name
                ] += 1
                continue

            assert (
                len(internal_transactions) <= 1
            ), f"Multiple internal transactions detected for {normal_transaction.function_name}, {normal_transaction.tx_hash}"

            internal_transaction = (
                internal_transactions[0] if internal_transactions else None
            )

            if normal_transaction.is_error():
                skip_transaction_reasons.error += 1
                continue

            assert len(erc20_transactions) > 0, "No ERC20 transactions found for swap"

            if not SwapTransactionBundle.is_valid_count_sub_transactions(
                normal_transaction, erc20_transactions, internal_transaction
            ):
                skip_transaction_reasons.not_valid_count_sub_transactions += 1
                continue

            swap_tranaction_bundle = SwapTransactionBundle(
                self.owner_address,
                normal_transaction,
                erc20_transactions,
                internal_transaction,
            )

            if not swap_tranaction_bundle.is_valid():
                skip_transaction_reasons.not_valid_bundle += 1
                continue

            swap_transaction_result = (
                SwapTransactionAnalyzer.get_swap_transaction_result(
                    swap_tranaction_bundle
                )
            )
            swap_transaction_results.append(swap_transaction_result)

        return (
            sorted(swap_transaction_results, key=lambda x: x.timestamp),
            skip_transaction_reasons,
        )

    def _create_txs_by_hash(self):
        txs_by_hash = defaultdict(list)
        for tx in (
            self.normal_transactions
            + self.erc20_transactions
            + self.internal_transactions
        ):
            txs_by_hash[tx.tx_hash].append(tx)
        return txs_by_hash
