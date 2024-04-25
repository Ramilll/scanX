from typing import List

from dataclasses import dataclass

from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction


@dataclass
class TransactionCount:
    normal_count: int
    erc20_count: int
    internal_count: int


def get_transaction_count_by_same_hash(
    transactions: List[NormalTransaction | ERC20Transaction | InternalTransaction],
) -> TransactionCount:
    normal_count = 0
    erc20_count = 0
    internal_count = 0
    for tx in transactions:
        if isinstance(tx, NormalTransaction):
            normal_count += 1
        elif isinstance(tx, ERC20Transaction):
            erc20_count += 1
        elif isinstance(tx, InternalTransaction):
            internal_count += 1
        else:
            raise ValueError(f"Unknown transaction type: {type(tx)}")
    return TransactionCount(
        normal_count=normal_count,
        erc20_count=erc20_count,
        internal_count=internal_count,
    )


def get_transaction_count(
    normal_transactions: List[NormalTransaction],
    erc20_transactions: List[ERC20Transaction],
    internal_transactions: List[InternalTransaction],
) -> TransactionCount:
    return TransactionCount(
        normal_count=len(normal_transactions),
        erc20_count=len(erc20_transactions),
        internal_count=len(internal_transactions),
    )
