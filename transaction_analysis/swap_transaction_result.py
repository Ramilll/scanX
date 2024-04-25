from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Token:
    name: str
    symbol: str
    decimal: int
    address: str

    def __str__(self):
        # Ensures that each Token has a unique string representation
        return f"{self.name} ({self.symbol}) at {self.address}"


@dataclass
class SwapTransactionResult:
    owner_address: str
    function_name: str
    token: Token
    swap_hash: str
    block_number: int
    timestamp: int
    router_address: str
    token_amount: float
    eth_amount: float
    transaction_fee: float
    direction: str  # 'buy' or 'sell'

    def eth_dir_sign(self) -> int:
        return -1 if self.direction == "buy" else 1

    def token_dir_sign(self) -> int:
        return 1 if self.direction == "buy" else -1

    def to_json(self) -> dict:
        """Converts the dataclass to a JSON-serializable dictionary."""
        return asdict(self)
