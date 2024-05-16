from transaction.swap_transaction_bundle import SwapTransactionBundle
from transaction_analysis.swap_transaction_result import SwapTransactionResult, Token


class SwapTransactionAnalyzer:
    @staticmethod
    def get_swap_transaction_result(
        bundle: SwapTransactionBundle,
    ) -> SwapTransactionResult:
        """
        Analyzes a swap transaction bundle to produce a summarized result of the swap operation.

        Args:
            bundle (SwapTransactionBundle): The bundle containing all related swap transactions.

        Returns:
            SwapTransactionResult: An object detailing the results of the swap transaction.
        """
        # Calculate net ETH and token results based on transaction directions
        eth_result = sum(
            bundle.get_transaction_dir(tx) * tx.value_in_eth()
            for tx in [bundle.normal_transaction, bundle.internal_transaction]
            if tx is not None
        )

        token_result = sum(
            bundle.get_transaction_dir(erc20)
            * erc20.transaction_value_in_native_tokens()
            for erc20 in bundle.erc20_transactions
        )

        # Construct the swap transaction result using properties from the bundle
        return SwapTransactionResult(
            owner_address=bundle.owner_address,
            function_name=bundle.function_name,
            token=Token(
                name=bundle.token_name,
                symbol=bundle.token_symbol,
                decimals=bundle.token_decimal,
                address=bundle.get_token_address(),
            ),
            swap_hash=bundle.swap_hash,
            block_number=bundle.block_number,
            timestamp=bundle.timestamp,
            router_address=bundle.router_address,
            token_amount=abs(token_result),
            eth_amount=abs(eth_result),
            transaction_fee=bundle.transaction_fee_eth,
            direction="buy" if eth_result < 0 else "sell",
        )
