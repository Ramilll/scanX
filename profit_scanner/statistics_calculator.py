from dataclasses import dataclass, asdict, field
from typing import Dict, List
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from transaction_analysis.swap_transaction_result import SwapTransactionResult
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
    per_coin_stats: Dict[str, CoinStatistics]

    def to_json(self) -> dict:
        return asdict(self)


class StatisticsCalculator:
    @staticmethod
    def process(
        owner_address: str, transactions: List[SwapTransactionResult]
    ) -> StatisticsResult:
        coin_stats_by_name = defaultdict(CoinStatistics)
        for swap_transaction in transactions:
            coin_stats = coin_stats_by_name[swap_transaction.token_name]
            coin_stats.trading_volume_eth += swap_transaction.eth_amount

            coin_stats.eth_saldo += (
                swap_transaction.eth_dir_sign() * swap_transaction.eth_amount
            )
            coin_stats.token_saldo += (
                swap_transaction.token_dir_sign() * swap_transaction.token_amount
            )
            coin_stats.last_transaction_time = max(
                coin_stats.last_transaction_time,
                datetime.fromtimestamp(swap_transaction.timestamp),
            )
            coin_stats.first_transaction_time = min(
                coin_stats.first_transaction_time,
                datetime.fromtimestamp(swap_transaction.timestamp),
            )
            coin_stats.num_deals += 1
            coin_stats.num_buy_deals += swap_transaction.direction == "buy"
            coin_stats.num_sell_deals += swap_transaction.direction == "sell"

        del_token_names = []
        for token_name in coin_stats_by_name.keys():
            print(token_name)
            if coin_stats_by_name[token_name].token_saldo < 0:
                del_token_names.append(token_name)

        for token_name in del_token_names:
            coin_stats_by_name.pop(token_name)

        stat_result = StatisticsResult(
            owner_address=owner_address,
            total_trading_volume_eth=sum(
                coin_stats.trading_volume_eth
                for coin_stats in coin_stats_by_name.values()
            ),
            last_transaction_time=max(
                coin_stats.last_transaction_time
                for coin_stats in coin_stats_by_name.values()
            ),
            first_transaction_time=min(
                coin_stats.first_transaction_time
                for coin_stats in coin_stats_by_name.values()
            ),
            per_coin_stats=dict(coin_stats_by_name),
        )
        return stat_result
