from typing import List, Tuple

from transaction.erc20_transaction import ERC20Transaction
from transaction.internal_transaction import InternalTransaction
from transaction.normal_transaction import NormalTransaction
from utils.etherscan_client import EtherscanClient


class TransactionLoader:
    """Class to load different types of transactions from Etherscan for a given owner address."""

    ETHERSCAN_CLIENT = EtherscanClient()

    @classmethod
    def load_transactions(
        cls,
        owner_address: str,
    ) -> Tuple[
        List[NormalTransaction], List[ERC20Transaction], List[InternalTransaction]
    ]:
        """
        Loads and returns the history of normal, ERC20, and internal transactions for a given owner address.

        Args:
            owner_address (str): The Ethereum address to query transaction histories for.

        Returns:
            Tuple[List[NormalTransaction], List[ERC20Transaction], List[InternalTransaction]]:
            A tuple containing lists of normal transactions, ERC20 transactions, and internal transactions.
        """
        normal_transactions = [
            NormalTransaction(tx)
            for tx in cls.ETHERSCAN_CLIENT.get_normal_transaction_history(owner_address)
        ]
        erc20_transactions = [
            ERC20Transaction(tx)
            for tx in cls.ETHERSCAN_CLIENT.get_erc20_transaction_history(owner_address)
        ]
        internal_transactions = [
            InternalTransaction(tx)
            for tx in cls.ETHERSCAN_CLIENT.get_internal_transaction_history(
                owner_address
            )
        ]
        return normal_transactions, erc20_transactions, internal_transactions
