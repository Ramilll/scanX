from enum import Enum

from transaction_analysis.transaction_pattern import TransactionPattern


class SwapFunctionName(Enum):
    swap_eth_for_exact_tokens = (
        "swapETHForExactTokens(uint256 amountOut, address[] path, address to, uint256 deadline)",
        TransactionPattern(1, 1, 1),
    )
    swap_exact_eth_for_tokens = (
        "swapExactETHForTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline)",
        TransactionPattern(1, 1, 0),
    )
    swap_exact_tokens_for_eth_supporting_fee_on_transfer_tokens = (
        "swapExactTokensForETHSupportingFeeOnTransferTokens(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline)",
        TransactionPattern(1, [1, 2], 1),
    )
    swap_exact_eth_for_tokens_supporting_fee_on_transfer_tokens = (
        "swapExactETHForTokensSupportingFeeOnTransferTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline)",
        TransactionPattern(1, 1, 0),
    )

    def __init__(self, function_signature, transaction_pattern):
        self._function_signature = function_signature
        self._transaction_pattern = transaction_pattern

    @property
    def signature(self):
        return self._function_signature

    @property
    def pattern(self):
        return self._transaction_pattern

    def is_valid_transaction_count(
        self, normal_transactions, erc20_transactions, internal_transaction
    ) -> bool:
        return self.pattern.validate(
            normal_transactions, erc20_transactions, internal_transaction
        )


def is_swap(function_name: str) -> bool:
    return any(
        function_name == swap_function.signature for swap_function in SwapFunctionName
    )
