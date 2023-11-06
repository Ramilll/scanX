from utils.constants import WEI_IN_ETH
from utils.transaction.base_transaction import BaseTransaction


class InternalTransaction(BaseTransaction):
    """
    Class for processing output from get_internal_transaction_history
    """

    def __init__(self, transaction: dict) -> None:
        super().__init__(transaction)
        self.transaction_name = "internal_transaction"
        self.is_error = int(transaction["isError"])
        self.err_code = transaction["errCode"]
        self.trace_id = transaction["traceId"]
        self.type = transaction["type"]

    def value_in_eth(self) -> float:
        return self.value / WEI_IN_ETH
