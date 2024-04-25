from dataclasses import dataclass
from typing import List, Optional

from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction
from transaction_analysis.swap_function_name import is_swap, SwapFunctionName


@dataclass
class SwapTransactionBundle:
    """
    Represents a bundle of transactions associated with a cryptocurrency swap operation.
    """

    normal_transaction: NormalTransaction
    erc20_transactions: List[ERC20Transaction]
    internal_transaction: Optional[InternalTransaction]

    def __init__(
        self,
        owner_address: str,
        normal_transaction: NormalTransaction,
        erc20_transactions: List[ERC20Transaction],
        internal_transaction: Optional[InternalTransaction],
    ):
        self.owner_address = owner_address
        self.normal_transaction = normal_transaction
        self.erc20_transactions = erc20_transactions
        self.internal_transaction = internal_transaction

        if not erc20_transactions:
            raise ValueError("ERC20 transactions list cannot be empty.")

    def is_valid(self) -> bool:
        """
        Checks if the swap transaction is valid based on hash, function name, and success status.
        """
        return (
            self._check_is_valid_hash()
            and self._check_is_valid_function_name()
            and self._check_swap_is_successful()
            and self._check_same_contract_address()
        )

    @property
    def swap_hash(self) -> str:
        return self.normal_transaction.tx_hash

    @property
    def function_name(self) -> str:
        return self.normal_transaction.function_name

    @property
    def block_number(self) -> int:
        return self.normal_transaction.block_number

    @property
    def timestamp(self) -> int:
        return self.normal_transaction.timestamp

    @property
    def router_address(self) -> str:
        return self.normal_transaction.to_address

    @property
    def transaction_fee_eth(self) -> float:
        return self.erc20_transactions[0].transaction_fee_in_eth()

    @property
    def token_name(self) -> str:
        token_name = self.erc20_transactions[0].token_name
        for erc_20_transaction in self.erc20_transactions:
            assert (
                token_name == erc_20_transaction.token_name
            ), f"Different token names for {self.swap_hash}"
        return token_name

    @property
    def token_symbol(self) -> str:
        token_symbol = self.erc20_transactions[0].token_symbol
        for erc_20_transaction in self.erc20_transactions:
            assert (
                token_symbol == erc_20_transaction.token_symbol
            ), "Different token symbols"
        return token_symbol

    @property
    def token_decimal(self) -> int:
        token_decimal = self.erc20_transactions[0].token_decimal
        for erc_20_transaction in self.erc20_transactions:
            assert (
                token_decimal == erc_20_transaction.token_decimal
            ), "Different token decimals"
        return token_decimal

    def get_transaction_dir(
        self, transaction: NormalTransaction | InternalTransaction | ERC20Transaction
    ) -> int:
        if transaction.from_address.lower() == self.owner_address.lower():
            return -1
        elif transaction.to_address.lower() == self.owner_address.lower():
            return 1
        return 0

    def get_token_address(self) -> str:
        if self.erc20_transactions:
            return self.erc20_transactions[0].contract_address
        raise ValueError("No ERC20 transactions found.")

    def _check_is_valid_hash(self) -> bool:
        swap_hash = self.normal_transaction.tx_hash
        return all(
            swap_hash == tx.tx_hash
            for tx in self.erc20_transactions
            + ([self.internal_transaction] if self.internal_transaction else [])
        )

    def _check_is_valid_function_name(self) -> bool:
        return is_swap(self.normal_transaction.function_name)

    def _check_swap_is_successful(self) -> bool:
        return not self.normal_transaction.is_error()

    def _check_same_contract_address(self) -> bool:
        return all(
            self.erc20_transactions[0].contract_address == tx.contract_address
            for tx in self.erc20_transactions
        )

    @staticmethod
    def is_valid_count_sub_transactions(
        normal_transaction: NormalTransaction,
        erc20_transactions: List[ERC20Transaction],
        internal_transaction: Optional[InternalTransaction],
    ) -> bool:
        """
        Validates the count of normal, ERC20, and internal transactions against expected patterns defined for the swap function.
        """
        function_enum = next(
            (
                func
                for func in SwapFunctionName
                if func.signature == normal_transaction.function_name
            ),
            None,
        )
        if not function_enum:
            return

        return (
            function_enum.is_valid_transaction_count(
                [normal_transaction],
                erc20_transactions,
                [internal_transaction] if internal_transaction else [],
            ),
            f"Invalid count of sub transactions for {normal_transaction.function_name}, tx_hash: {normal_transaction.tx_hash} actual count normal: 1, erc20: {len(erc20_transactions)}, internal: {1 if internal_transaction else 0}",
        )
