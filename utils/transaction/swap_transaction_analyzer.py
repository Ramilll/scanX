from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from utils.transaction.erc20_transaction import ERC20Transaction
from utils.transaction.internal_transaction import InternalTransaction
from utils.transaction.normal_transaction import NormalTransaction


class SwapFunctionName(Enum):
    swap_eth_for_exact_tokens = "swapETHForExactTokens(uint256 amountOut, address[] path, address to, uint256 deadline)"
    swap_exact_eth_for_tokens = "swapExactETHForTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline)"
    swap_exact_tokens_for_eth_supporting_fee_on_transfer_tokens = "swapExactTokensForETHSupportingFeeOnTransferTokens(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)"


SWAP_FUNCTION_NAMES = [swap.value for swap in SwapFunctionName]


@dataclass
class SwapTransactionResult:
    owner_address: str
    function_name: str
    swap_hash: str
    block_number: int
    timestamp: int
    router_address: str
    token_address: str
    token_amount: float
    eth_amount: float
    transaction_fee: float
    direction: str  # buy or sell


# swap_eth_for_exact_tokens -> 1 normal, 1 erc20, 1 internal
# swap_exact_eth_for_tokens -> 1 normal, 1 erc20
# swap_exact_tokens_for_eth_supporting_fee_on_transfer_tokens -> 1 normal, 1 internal, 1/2 erc20


class SwapTransactionAnalyzer:
    def __init__(
        self,
        owner_address: str,
        normal_transaction: NormalTransaction,
        erc20_transactions: List[ERC20Transaction],
        internal_transaction: Optional[InternalTransaction],
    ) -> None:
        self.owner_address: str = owner_address
        self.swap_hash: str = normal_transaction.tx_hash
        self.swap_function_name: str = normal_transaction.function_name
        self.swap_block_number: int = (
            normal_transaction.block_number
        )  # same block number for all transactions
        self.swap_timestamp: int = (
            normal_transaction.timestamp
        )  # same timestamp for all transactions
        self.router_address: str = normal_transaction.to_address
        self.token_address: str = erc20_transactions[0].contract_address

        self.normal_transaction: NormalTransaction = normal_transaction
        self.erc_20_transactions: List[ERC20Transaction] = erc20_transactions
        self.internal_transaction: Optional[InternalTransaction] = internal_transaction

        self.check_transactions_have_same_hash()
        self.check_swap_function_name_is_swap()
        self.check_swap_is_successful()  # only takes not failed swaps

    def check_transactions_have_same_hash(self):
        "If hash is the same => same block number and timestamp"
        assert (
            self.normal_transaction.tx_hash == self.swap_hash
        ), "Wrong normal transaction hash"
        assert (
            self.erc_20_transaction.tx_hash == self.swap_hash
        ), "Wrong erc20 transaction hash"
        for internal_transaction in self.internal_transactions:
            assert (
                internal_transaction.tx_hash == self.swap_hash
            ), "Wrong internal transaction hash"

    def check_swap_function_name_is_swap(self):
        assert (
            self.normal_transaction.function_name in SWAP_FUNCTION_NAMES
        ), "Wrong function name for normal transaction"

    def check_swap_is_successful(self):
        assert self.normal_transaction.is_error == 0, "Normal transaction is error"

    def get_transaction_dir(self, transaction) -> int:
        if transaction.from_address == self.owner_address:
            return -1
        elif transaction.to_address == self.owner_address:
            return 1
        else:
            return 0

    def get_swap_transaction_result(self) -> SwapTransactionResult:
        eth_result = 0
        token_result = 0
        transaction_fee_in_eth = self.erc_20_transactions[0].transaction_fee_in_eth()

        eth_result += (
            self.get_transaction_dir(self.normal_transaction)
            * self.normal_transaction.value_in_eth()
        )
        if self.internal_transaction:
            eth_result += (
                self.get_transaction_dir(self.internal_transaction)
                * self.internal_transaction.value_in_eth()
            )
        for tx in self.erc_20_transactions:
            token_result += self.get_transaction_dir(tx) * tx.token_amount

        swap_result = SwapTransactionResult(
            owner_address=self.owner_address,
            function_name=self.swap_function_name,
            swap_hash=self.swap_hash,
            block_number=self.swap_block_number,
            timestamp=self.swap_timestamp,
            router_address=self.router_address,
            token_address=self.token_address,
            token_amount=abs(token_result),
            eth_amount=abs(eth_result),
            transaction_fee=transaction_fee_in_eth,
            direction="buy" if eth_result > 0 else "sell",
        )

        return swap_result
