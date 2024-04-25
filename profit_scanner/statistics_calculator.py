from dataclasses import dataclass, asdict, field, is_dataclass
import json
from typing import Dict, List
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from transaction_analysis.swap_transaction_result import SwapTransactionResult, Token
from dataclasses import dataclass, asdict, field
from typing import Dict, List
from datetime import datetime
import numpy as np
from collections import defaultdict


@dataclass
class CoinStatistics:
    trading_volume_eth: float = 0
    eth_saldo: float = 0
    token_saldo: float = 0
    first_transaction_time: datetime = datetime.max
    last_transaction_time: datetime = datetime.min
    num_deals: int = 0
    num_buy_deals: int = 0
    num_sell_deals: int = 0


@dataclass
class StatisticsResult:
    owner_address: str
    total_trading_volume_eth: float
    last_transaction_time: datetime
    first_transaction_time: datetime
    per_coin_stats: Dict[Token, CoinStatistics] = field(default_factory=dict)

    def to_dict(self) -> dict:
        # Manually create dictionary to handle complex types
        return {
            "owner_address": self.owner_address,
            "total_trading_volume_eth": self.total_trading_volume_eth,
            "last_transaction_time": self.last_transaction_time.isoformat(),
            "first_transaction_time": self.first_transaction_time.isoformat(),
            "per_coin_stats": {
                str(key): (
                    value.to_dict() if hasattr(value, "to_dict") else asdict(value)
                )
                for key, value in self.per_coin_stats.items()
            },
        }


class StatisticsCalculator:
    @staticmethod
    def process(
        owner_address: str, transactions: List[SwapTransactionResult]
    ) -> StatisticsResult:
        coin_stats_by_token: Dict[Token, CoinStatistics] = defaultdict(CoinStatistics)
        for swap_transaction in transactions:
            stats = coin_stats_by_token[swap_transaction.token]
            stats.trading_volume_eth += swap_transaction.eth_amount

            stats.eth_saldo += (
                swap_transaction.eth_dir_sign() * swap_transaction.eth_amount
            )
            stats.token_saldo += (
                swap_transaction.token_dir_sign() * swap_transaction.token_amount
            )
            stats.last_transaction_time = max(
                stats.last_transaction_time,
                datetime.fromtimestamp(swap_transaction.timestamp),
            )
            stats.first_transaction_time = min(
                stats.first_transaction_time,
                datetime.fromtimestamp(swap_transaction.timestamp),
            )
            stats.num_deals += 1
            stats.num_buy_deals += swap_transaction.direction == "buy"
            stats.num_sell_deals += swap_transaction.direction == "sell"

        del_token_names = []
        for token in coin_stats_by_token.keys():
            print(token)
            if coin_stats_by_token[token].token_saldo < 0:
                del_token_names.append(token)

        for token in del_token_names:
            coin_stats_by_token.pop(token)

        stat_result = StatisticsResult(
            owner_address=owner_address,
            total_trading_volume_eth=sum(
                stats.trading_volume_eth for stats in coin_stats_by_token.values()
            ),
            last_transaction_time=max(
                stats.last_transaction_time for stats in coin_stats_by_token.values()
            ),
            first_transaction_time=min(
                stats.first_transaction_time for stats in coin_stats_by_token.values()
            ),
            per_coin_stats=dict(coin_stats_by_token),
        )
        return stat_result
