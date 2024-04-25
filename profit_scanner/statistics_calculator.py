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
    pnl_percentage: float
    total_profit_eth: float
    total_profit_coin: float
    last_transaction_time: datetime
    first_transaction_time: datetime
    total_trade_volume_eth: float


@dataclass
class StatisticsResult:
    owner_address: str
    total_volume: float
    last_transaction_time: datetime
    first_transaction_time: datetime
    median_trade_time: Dict[str, datetime]
    average_buy_amount_eth: float
    average_sell_amount_eth: float
    overall_pnl_percentage: float
    sharp_ratio: Dict[str, float]
    per_coin_stats: Dict[str, CoinStatistics]

    def to_json(self) -> dict:
        return asdict(self)


def calculate_pnl(coin_data):
    if coin_data["total_bought"] == 0:
        return 0
    return (
        (coin_data["total_sold_eth"] - coin_data["total_bought_eth"])
        / coin_data["total_bought_eth"]
        * 100
    )


def calculate_sharp_ratio(pnl_list):
    if not pnl_list:
        return 0.0
    mean_return = np.mean(pnl_list)
    sd_return = np.std(pnl_list, ddof=1) if len(pnl_list) > 1 else 1
    return mean_return / sd_return


def calculate_statistics(transactions: List[SwapTransactionResult]) -> StatisticsResult:
    if not transactions:
        return None
    owner_address = transactions[0].owner_address
    coins_data = defaultdict(
        lambda: {
            "total_bought": 0,
            "total_sold": 0,
            "total_bought_eth": 0,
            "total_sold_eth": 0,
            "pnl_history": [],
            "times": [],
        }
    )
    total_volume = 0
    last_transaction_time = None
    first_transaction_time = None
    total_buy_eth = 0
    total_sell_eth = 0
    num_buys = 0
    num_sells = 0

    for txn in transactions:
        txn_time = datetime.fromtimestamp(txn.timestamp)
        if not first_transaction_time or txn_time < first_transaction_time:
            first_transaction_time = txn_time
        if not last_transaction_time or txn_time > last_transaction_time:
            last_transaction_time = txn_time

        total_volume += txn.eth_amount
        coins_data[txn.token_symbol]["times"].append(txn_time)
        if txn.direction == "buy":
            coins_data[txn.token_symbol]["total_bought"] += txn.token_amount
            coins_data[txn.token_symbol]["total_bought_eth"] += txn.eth_amount
            total_buy_eth += txn.eth_amount
            num_buys += 1
        elif txn.direction == "sell":
            coins_data[txn.token_symbol]["total_sold"] += txn.token_amount
            coins_data[txn.token_symbol]["total_sold_eth"] += txn.eth_amount
            total_sell_eth += txn.eth_amount
            num_sells += 1

    median_trade_times = {
        coin: np.median([time.timestamp() for time in data["times"]]).astype(datetime)
        for coin, data in coins_data.items()
    }

    per_coin_stats = {}
    sharp_ratios = {}
    for coin, data in coins_data.items():
        first_coin_txn_time = min(data["times"])
        last_coin_txn_time = max(data["times"])
        total_trade_volume_eth = data["total_bought_eth"] + data["total_sold_eth"]
        pnl_percentage = calculate_pnl(data)
        per_coin_stats[coin] = CoinStatistics(
            pnl_percentage=pnl_percentage,
            total_profit_eth=data["total_sold_eth"] - data["total_bought_eth"],
            total_profit_coin=data["total_sold"] - data["total_bought"],
            last_transaction_time=last_coin_txn_time,
            first_transaction_time=first_coin_txn_time,
            total_trade_volume_eth=total_trade_volume_eth,
        )
        sharp_ratios[coin] = calculate_sharp_ratio(data["pnl_history"])

    average_buy_amount_eth = total_buy_eth / num_buys if num_buys else 0
    average_sell_amount_eth = total_sell_eth / num_sells if num_sells else 0

    return StatisticsResult(
        owner_address=owner_address,
        total_volume=total_volume,
        last_transaction_time=last_transaction_time,
        first_transaction_time=first_transaction_time,
        median_trade_time=median_trade_times,
        average_buy_amount_eth=average_buy_amount_eth,
        average_sell_amount_eth=average_sell_amount_eth,
        overall_pnl_percentage=calculate_pnl(
            {
                "total_bought_eth": total_buy_eth,
                "total_sold_eth": total_sell_eth,
                "total_bought": num_buys,
                "total_sold": num_sells,
            }
        ),
        sharp_ratio=sharp_ratios,
        per_coin_stats=per_coin_stats,
    )
