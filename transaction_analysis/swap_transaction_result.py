from dataclasses import dataclass, asdict


@dataclass
class SwapTransactionResult:
    owner_address: str
    function_name: str
    token_name: str
    token_symbol: str
    token_decimal: int
    swap_hash: str
    block_number: int
    timestamp: int
    router_address: str
    token_address: str
    token_amount: float
    eth_amount: float
    transaction_fee: float
    direction: str  # 'buy' or 'sell'

    def to_json(self) -> dict:
        """Converts the dataclass to a JSON-serializable dictionary."""
        return asdict(self)
