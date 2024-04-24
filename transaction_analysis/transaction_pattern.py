from typing import List

from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction


class TransactionPattern:
    def __init__(self, normal_count, erc20_count, internal_count):
        # Allow both single integer values or tuples/lists for specifying counts
        self.normal_count = (
            normal_count if isinstance(normal_count, (list, tuple)) else [normal_count]
        )
        self.erc20_count = (
            erc20_count if isinstance(erc20_count, (list, tuple)) else [erc20_count]
        )
        self.internal_count = (
            internal_count
            if isinstance(internal_count, (list, tuple))
            else [internal_count]
        )

    def validate(
        self,
        normal_transactions: List[NormalTransaction],
        erc20_transactions: List[ERC20Transaction],
        internal_transactions: List[InternalTransaction],
    ) -> bool:
        # Validate each transaction count against the allowed values
        normal_count = len(normal_transactions)
        erc20_count = len(erc20_transactions)
        internal_count = len(internal_transactions)

        if not self._validate_count(normal_count, self.normal_count):
            return False
        if not self._validate_count(erc20_count, self.erc20_count):
            return False
        if not self._validate_count(internal_count, self.internal_count):
            return False

        return True

    def _validate_count(self, actual_count, expected_counts) -> bool:
        return actual_count in expected_counts
