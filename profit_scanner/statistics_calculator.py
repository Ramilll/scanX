from dataclasses import dataclass, asdict, field, fields, is_dataclass
import json
from typing import Dict, List
import numpy as np
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from transaction_analysis.swap_transaction_result import SwapTransactionResult, Token
from dataclasses import dataclass, asdict, field
from api_endpoints.uniswap_api import get_token_price
from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict


@dataclass
class CoinStatistics:
    trading_volume_eth: float = 0
    eth_saldo: float = 0
    token_saldo: float = 0
    eth_buy_volume: float = 0
    first_transaction_time: datetime = datetime.max
    last_transaction_time: datetime = datetime.min
    num_deals: int = 0
    num_buy_deals: int = 0
    num_sell_deals: int = 0


@dataclass
class StatisticsResult:
    owner_address: str
    total_trading_volume_eth: float
    eth_saldo: float
    total_buy_eth_volume: float
    profitable_coins_percent: float
    unprofitable_coins_percent: float
    sharpe_ratio: float
    average_coin_profit_eth: float
    average_coin_loss_eth: float
    num_deals: int
    num_buy_deals: int
    num_sell_deals: int
    roi_percent: float
    yearly_roi_percent: float
    average_roi_per_coin_percent: float
    average_profitable_roi_per_coin_percent: float
    average_unprofitable_roi_per_coin_percent: float
    average_num_deals_per_coin: float
    last_transaction_time: datetime
    first_transaction_time: datetime
    per_coin_stats: Dict[Token, CoinStatistics] = field(default_factory=dict)

    def to_dict(self) -> dict:
        data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, datetime):
                # Convert datetime to ISO format string
                data[field.name] = value.isoformat()
            elif isinstance(value, dict):
                # Handle dictionaries, especially with custom object keys
                data[field.name] = {
                    str(key): val.to_dict() if hasattr(val, "to_dict") else asdict(val)
                    for key, val in value.items()
                }
            elif is_dataclass(value):
                # Recursively convert dataclass fields to dict
                data[field.name] = asdict(value)
            else:
                # Assign other types as is
                data[field.name] = value
        return data


class StatisticsCalculator:
    @staticmethod
    def process(
        owner_address: str, transactions: List[SwapTransactionResult]
    ) -> StatisticsResult | None:
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
            stats.eth_buy_volume += (
                swap_transaction.eth_amount
                if swap_transaction.direction == "buy"
                else 0
            )

        del_token_names = []
        for token in coin_stats_by_token.keys():
            # if token position is below zero -> remove it
            if coin_stats_by_token[token].token_saldo < 0:
                print(f"Removing token {token} from statistics")
                del_token_names.append(token)

        for token in del_token_names:
            coin_stats_by_token.pop(token)

        if len(coin_stats_by_token) == 0:
            return None

        eth_saldos = np.array(
            [stats.eth_saldo for stats in coin_stats_by_token.values()]
        )
        profitable_coins_percent = np.sum(eth_saldos > 0) / len(eth_saldos) * 100
        unprofitable_coins_percent = np.sum(eth_saldos < 0) / len(eth_saldos) * 100
        sharpe_ratio = np.mean(eth_saldos) / np.std(eth_saldos)
        average_coin_profit = np.mean(eth_saldos[eth_saldos > 0])
        average_coin_loss = np.mean(eth_saldos[eth_saldos < 0])
        total_trading_volume_eth = sum(
            stats.trading_volume_eth for stats in coin_stats_by_token.values()
        )
        eth_saldo = sum(stats.eth_saldo for stats in coin_stats_by_token.values())
        first_transaction_time = min(
            stats.first_transaction_time for stats in coin_stats_by_token.values()
        )
        last_transaction_time = max(
            stats.last_transaction_time for stats in coin_stats_by_token.values()
        )

        total_eth_buy_volume = sum(
            stats.eth_buy_volume for stats in coin_stats_by_token.values()
        )
        roi = eth_saldo / total_eth_buy_volume
        active_time = timedelta(
            days=(last_transaction_time - first_transaction_time).days
        )
        yearly_roi = roi / active_time.days * 365
        num_deals = sum(stats.num_deals for stats in coin_stats_by_token.values())
        num_buy_deals = sum(
            stats.num_buy_deals for stats in coin_stats_by_token.values()
        )
        num_sell_deals = sum(
            stats.num_sell_deals for stats in coin_stats_by_token.values()
        )
        average_num_deals_per_coin = np.mean(
            [stats.num_deals for stats in coin_stats_by_token.values()]
        )
        average_roi_per_coin = np.mean(
            [
                stats.eth_saldo / stats.eth_buy_volume
                for stats in coin_stats_by_token.values()
            ]
        )
        average_profitable_roi_per_coin = np.mean(
            [
                stats.eth_saldo / stats.eth_buy_volume
                for stats in coin_stats_by_token.values()
                if stats.eth_saldo > 0
            ]
        )
        average_unprofitable_roi_per_coin = np.mean(
            [
                stats.eth_saldo / stats.eth_buy_volume
                for stats in coin_stats_by_token.values()
                if stats.eth_saldo < 0
            ]
        )

        stat_result = StatisticsResult(
            owner_address=owner_address,
            total_trading_volume_eth=total_trading_volume_eth,
            eth_saldo=eth_saldo,
            total_buy_eth_volume=total_eth_buy_volume,
            profitable_coins_percent=profitable_coins_percent,
            unprofitable_coins_percent=unprofitable_coins_percent,
            sharpe_ratio=sharpe_ratio,
            average_coin_profit_eth=average_coin_profit,
            average_coin_loss_eth=average_coin_loss,
            num_deals=num_deals,
            num_buy_deals=num_buy_deals,
            num_sell_deals=num_sell_deals,
            average_num_deals_per_coin=average_num_deals_per_coin,
            roi_percent=roi * 100,
            yearly_roi_percent=yearly_roi * 100,
            average_roi_per_coin_percent=average_roi_per_coin * 100,
            average_profitable_roi_per_coin_percent=average_profitable_roi_per_coin
            * 100,
            average_unprofitable_roi_per_coin_percent=average_unprofitable_roi_per_coin
            * 100,
            last_transaction_time=last_transaction_time,
            first_transaction_time=first_transaction_time,
            per_coin_stats=dict(coin_stats_by_token),
        )
        return stat_result
