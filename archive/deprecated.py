import datetime
import json
import logging
import math
import os
import pickle
import time
from operator import itemgetter

import cryptowatch as cw
import numpy as np
import plotly.graph_objects as go
import requests
import web3
from sortedcontainers import SortedList
from tqdm import tqdm
from uniswap import Uniswap
from web3 import Web3

ALCHEMY_KEY = "https://eth-mainnet.g.alchemy.com/v2/939THemxLlThMsjblHUIWl89plPtayML"
ETHERSCAN_API_KEY = "2ZJPPN1PK77474N26RUXHBXTZ4RC19Q4NR"

print("### Configuration")
w3 = Web3(Web3.HTTPProvider(ALCHEMY_KEY))
print("Alchemy connected: ", w3.is_connected())
LATEST_BLOCK = w3.eth.block_number
print("Current block No: ", LATEST_BLOCK)

UNI_ABI = json.load(open("uni_abi.json", "r"))

factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
factory_contract = w3.eth.contract(address=factory_address, abi=UNI_ABI)
eth_address = Web3.to_checksum_address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
eth_decimals = 18


def get_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def get_pool_in_usd(token_address, blockno=LATEST_BLOCK):
    token_address = Web3.to_checksum_address(token_address)
    pair_address = factory_contract.functions.getPair(token_address, eth_address).call()
    pair_address = Web3.to_checksum_address(pair_address)
    contract = w3.eth.contract(address=pair_address, abi=UNI_ABI)

    try:
        reserves = contract.functions.getReserves().call(block_identifier=blockno)
    except Exception as e:
        logging.info(e)
        logging.info(f"Pool doesnt found: {token_address}")
        return 0, pair_address

    reserve0 = reserves[0]
    reserve1 = reserves[1]

    token0_address = contract.functions.token0().call()
    token1_address = contract.functions.token1().call()

    if token0_address == eth_address:
        pool_eth = reserve0 / (10**eth_decimals)
    elif token1_address == eth_address:
        pool_eth = reserve1 / (10**eth_decimals)
    return pool_eth, pair_address


def get_native_history(user_address, start_blockno=0, end_blockno=LATEST_BLOCK):
    params = {
        "module": "account",
        "action": "txlist",
        "address": user_address,
        "page": 1,
        "offset": 0,
        "startblock": start_blockno,
        "endblock": end_blockno,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get("https://api.etherscan.io/api", params=params)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["result"]

    logging.info(f"Request failed with status code {response.status_code}")
    logging.info(response.text)
    logging.info("\n")
    return False


def get_erc_history(user_address, start_blockno=0, end_blockno=LATEST_BLOCK):
    params = {
        "module": "account",
        "action": "tokentx",
        "address": user_address,
        "page": "1",
        "offset": "0",
        "startblock": start_blockno,
        "endblock": end_blockno,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get("https://api.etherscan.io/api", params=params)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["result"]

    logging.info(f"Request failed with status code {response.status_code}")
    logging.info(response.text)
    logging.info("\n")
    return False


def get_ether_balance_by_block(user_address, blockno=LATEST_BLOCK):
    user_address = Web3.to_checksum_address(user_address)
    return w3.eth.get_balance(user_address, block_identifier=int(blockno)) / (10**18)


def check_if_contract(address):
    checksum = Web3.to_checksum_address(address)
    code = w3.eth.get_code(checksum)
    if code:
        return True
    return False


def get_route_history(route_address, page_number, blockno=LATEST_BLOCK):
    params = {
        "module": "account",
        "action": "tokentx",
        "address": route_address,
        "page": page_number,
        "offset": 10000,
        "startblock": "0",
        "endblock": blockno,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get("https://api.etherscan.io/api", params=params)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["result"]

    logging.info(f"Request failed with status code {response.status_code}")
    logging.info(response.text)
    logging.info("\n")
    return False


def get_blockno_by_timestamp(timestamp):
    params = {
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get("https://api.etherscan.io/api", params=params)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["result"]

    logging.info(f"Request failed with status code {response.status_code}")
    logging.info(response.text)
    logging.info("\n")
    return False


def get_price(token_address, decimals):
    token_address = Web3.to_checksum_address(token_address)
    try:
        version = 3
        uniswap = Uniswap(
            address=None, private_key=None, version=version, provider=ALCHEMY_KEY
        )
        price_out = uniswap.get_price_output(eth, token_address, 10**decimals)
    except:
        try:
            version = 2
            uniswap = Uniswap(
                address=None, private_key=None, version=version, provider=ALCHEMY_KEY
            )
            price_out = uniswap.get_price_output(eth, token_address, 10**decimals)
        except:
            price_out = 0
    return price_out / (10**decimals_eth)


def nearest_timestamp(input_timestamp, sorted_timestamps):
    idx = sorted_timestamps.bisect_left(input_timestamp)
    if idx == 0:
        return 0
    if idx == len(sorted_timestamps):
        return -1
    before = sorted_timestamps[idx - 1]
    after = sorted_timestamps[idx]
    if after - input_timestamp < input_timestamp - before:
        return idx
    else:
        return idx - 1


def get_token_price(token_symbol, exclude_exchanges=[], ohlc_after=1655446620):
    resp = cw.assets.get(token_symbol)

    token = json.loads(resp._http_response.text)["result"]

    exchange_name = ""
    for el in token["markets"]["base"]:
        if el["exchange"] in exclude_exchanges:
            continue
        if (
            f"{token_symbol.lower()}usdt" == el["pair"]
            or f"{token_symbol.lower()}usdc" == el["pair"]
        ):
            exchange_name = el["exchange"]
            pair = el["pair"]
            if (
                "coinbase" in el["exchange"]
                or "binance" in el["exchange"]
                or "kraken" in el["exchange"]
                or "okx" in el["exchange"]
            ):
                break

    if exchange_name:
        resp = cw.markets.get(
            f"{exchange_name.upper()}:{pair.upper()}",
            ohlc=True,
            periods=["1h"],
            ohlc_after=ohlc_after,
        )
        history = json.loads(resp._http_response.text)["result"]
        history = history[list(history.keys())[0]]

        timestamps = [x[0] for x in history]
        open_values = [x[1] for x in history]

        timestamps = SortedList(timestamps)
        closest_ts_idx = nearest_timestamp(1688546207, timestamps)
        diff_seconds = abs(timestamps[closest_ts_idx] - 1688546207)
        three_days_seconds = 3 * 24 * 60 * 60
        if diff_seconds > three_days_seconds:
            token_history = get_token_price(
                token_symbol, exclude_exchanges + [exchange_name], ohlc_after=ohlc_after
            )
        else:
            token_history = {"timestamps": timestamps, "values": open_values}
    else:
        logging.info("Coinbase hasn't found")
        logging.info("\n")
        return {}
    return token_history


def get_token_balance_by_block(user_address, token_address, blockno=LATEST_BLOCK):
    user_address = Web3.to_checksum_address(user_address)
    token_address = Web3.to_checksum_address(token_address)

    if os.path.exists("src/abi.json"):
        token_abi = json.load(open("src/abi.json", "r"))
    else:
        token_abi = json.load(open("abi.json", "r"))
    token = w3.eth.contract(
        address=token_address, abi=token_abi
    )  # declaring the token contract
    try:
        token_balance = token.functions.balanceOf(user_address).call(
            block_identifier=blockno
        )  # returns int with balance, without decimals
    except web3.exceptions.ABIFunctionNotFound as e:
        logging.info("Error {e}")
    return token_balance


def get_token_info(contract_address):
    params = {
        "module": "token",
        "action": "tokeninfo",
        "contractaddress": contract_address,
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get("https://api.etherscan.io/api", params=params)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["result"]

    logging.info(f"Request failed with status code {response.status_code}")
    logging.info(response.text)
    logging.info("\n")
    return False


def get_token_holders(contract_address):
    params = {
        "module": "token",
        "action": "tokenholderlist",
        "contractaddress": contract_address,
        "page": "1",
        "offset": "0",
        "apikey": ETHERSCAN_API_KEY,
    }

    response = requests.get("https://api.etherscan.io/api", params=params)

    if response.status_code == 200:
        json_response = response.json()
        return json_response["result"]

    logging.info(f"Request failed with status code {response.status_code}")
    logging.info(response.text)
    logging.info("\n")
    return False


def get_sell_price(token_address, token_decimals, token_amount):
    token_amount = int(token_amount * 10**token_decimals)
    token_address = Web3.to_checksum_address(token_address)
    try:
        version = 2
        uniswap = Uniswap(
            address=None, private_key=None, version=version, provider=ALCHEMY_KEY
        )
        price_out = uniswap.get_price_input(token_address, eth_address, token_amount)
        return price_out / (10**eth_decimals)
    except Exception as e:
        try:
            version = 3
            uniswap = Uniswap(
                address=None, private_key=None, version=version, provider=ALCHEMY_KEY
            )

            price_out = uniswap.get_price_input(
                token_address, eth_address, token_amount
            )
            return price_out / (10**eth_decimals)
        except Exception as e:
            return None


def main(
    user_address,
    ts_after,
    UNTIL_BLOCKNO,
    logger,
    TOKEN_HOLDERS_TRESHOLD,
    MARKET_CAP_TRESHOLD,
):
    handler = logging.FileHandler(os.path.join("log.txt"), "w")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    logging.info(f"Start date {get_date(ts_after)}")
    start_blockno = get_blockno_by_timestamp(ts_after)
    all_txs = get_erc_history(
        user_address, start_blockno=start_blockno, end_blockno=UNTIL_BLOCKNO
    )

    unique_addresses = set([tx["contractAddress"] for tx in all_txs])

    lowest_blocks = {}

    for data in tqdm(all_txs, "Extracting blocks"):
        addr, block = data["contractAddress"], int(data["blockNumber"])
        lowest_blocks[addr] = min(block, lowest_blocks.get(addr, float("inf")))

    print("Unique tokens ", len(unique_addresses))
    # is_scam = {}
    # token_address_to_info = {}
    # for addr in tqdm(unique_addresses, 'Checking for scam'):
    #   pass
    # pool_in_eth = get_pool_in_usd(addr, lowest_blocks[addr])
    # token_address_to_info[addr] = {}
    # token_address_to_info[addr]['pool_in_eth'] = pool_in_eth
    # info = get_token_info(addr)
    # if info:
    #   info = info[0]

    # token_price = float(info['tokenPriceUSD'])
    # total_supply = int(info['totalSupply'])
    # divisor = int(info['divisor'])

    # market_cap = token_price * (total_supply / (10 ** divisor))
    # if TOKEN_HOLDERS_TRESHOLD:
    #   is_scam[addr] = True
    #   continue

    # holders = get_token_holders(addr)
    # is_scam[addr] = len(holders) < TOKEN_HOLDERS_TRESHOLD
    # is_scam[addr] = False
    # print(f"Token {addr}:\nHolders {len(holders)}\nPrice in USD {token_price}, Marketcap {market_cap}")

    for item in all_txs:
        item["timeStamp"] = int(item["timeStamp"])
    all_txs = sorted(all_txs, key=itemgetter("timeStamp"))

    ether_balance = 0
    prev_ether_balance = 0
    tx_hashes = []
    d_all = {}
    symbol2address = {}
    tokens = {}
    for i, tx in enumerate(tqdm(all_txs, "Processing txs")):
        token_symbol = tx["tokenSymbol"]
        if not token_symbol in symbol2address:
            symbol2address[token_symbol] = [
                tx["contractAddress"],
                int(tx["tokenDecimal"]),
            ]

        block_number = int(tx["blockNumber"])

        if tx["hash"] not in tx_hashes:
            tokens = {}
            tx_hashes.append(tx["hash"])
            prev_ether_balance = get_ether_balance_by_block(
                user_address, block_number - 1
            )
            ether_balance = get_ether_balance_by_block(user_address, block_number)
            gas = int(tx["gasPrice"]) * int(tx["gasUsed"]) / 10**18
            diff_ether = ether_balance - prev_ether_balance

        if "tokenName" in tx:
            tokens[token_symbol] = float(tx["value"]) / (10 ** int(tx["tokenDecimal"]))

        if ((i + 1) == len(all_txs)) or tx["hash"] != all_txs[i + 1]["hash"]:
            if (
                diff_ether == 0
                or diff_ether + gas == 0
                or abs(diff_ether) < 0.03
                or abs(diff_ether + gas) < 0.03
            ):
                continue
            else:
                if len(tokens) == 0:
                    continue
                elif len(tokens) > 1:
                    continue

            if token_symbol not in d_all:
                d_all[token_symbol] = {}

            token_symbol = list(tokens.keys())[0]
            value = list(tokens.values())[0]

            if tx["from"] == user_address:
                if (diff_ether + gas) < 0:
                    print(token_symbol, value, diff_ether, gas, tokens)
                    print("Unexpected behaviour")
                    print(tx["hash"])
                    continue

                if "amount" not in d_all[token_symbol]:
                    continue

                if value > d_all[token_symbol]["amount"]:
                    diff_ether = (diff_ether / value) * d_all[token_symbol]["amount"]
                    d_all[token_symbol]["amount"] -= d_all[token_symbol]["amount"]
                else:
                    d_all[token_symbol]["amount"] -= value

                if "sold" in d_all[token_symbol]:
                    d_all[token_symbol]["sold"] += diff_ether
                else:
                    d_all[token_symbol]["sold"] = diff_ether

            else:
                if (diff_ether - gas) > 0:
                    print(token_symbol, value, diff_ether, gas, tokens)
                    print("Unexpected behaviour")
                    print(tx["hash"])
                    continue

                if "bought" in d_all[token_symbol]:
                    d_all[token_symbol]["bought"] += abs(diff_ether)
                else:
                    d_all[token_symbol]["bought"] = abs(diff_ether)

                if "amount" not in d_all[token_symbol]:
                    d_all[token_symbol]["amount"] = 0
                d_all[token_symbol]["amount"] += value

    print(d_all)
    # exit(0)
    win_rate = 0
    overall = 0
    pnl_released = 0
    pnl_unreleased = 0

    for key, value in tqdm(d_all.items(), "Count stats"):
        overall += 1
        tokenB, tokenB_decimals = symbol2address[key]
        first_block = lowest_blocks[tokenB]
        pool_in_ether = get_pool_in_usd(tokenB, blockno=first_block)
        pool_in_ether_now = get_pool_in_usd(tokenB, blockno=LATEST_BLOCK)
        d_all[key]["pool_liq_now"] = pool_in_ether_now
        d_all[key]["pool_liq"] = pool_in_ether
        d_all[key]["first_block"] = first_block
        d_all[key]["addr"] = tokenB
        # price = get_price(tokenB,tokenB_decimals)
        # print(key, price)
        if "bought" in value and "sold" in value:
            pnl = value["sold"] - value["bought"]
            pnl_released += pnl

            d_all[key]["pnl"] = pnl
            d_all[key]["x_amount"] = pnl / value["bought"]

            if pnl > 0:
                win_rate += 1
        elif "bought" in value and "sold" not in value:
            cur_price = get_sell_price(tokenB, tokenB_decimals, value["bought"])
            if not cur_price:
                continue
            d_all[key]["unpnl"] = cur_price - value["bought"]
            pnl_unreleased += d_all[key]["unpnl"]
            if d_all[key]["unpnl"] > 0:
                win_rate += 1

    result = {
        "user_address": user_address,
        "tokens": d_all,
        "win_rate": win_rate / max(overall, 1),
        "tokens_amount": overall,
        "win_rate_amount": win_rate,
        "pnl_released": pnl_released,
        "pnl_unreleased": pnl_unreleased,
        "overall_txs": len(set([x["hash"] for x in all_txs])),
    }

    from pprint import pprint

    print("For ", user_address)
    # print('All tokens')
    # pprint(result['tokens'])

    # print('Scam percentage: ', result['scam_percentage'])
    # print(f'Percentage of good token trades: {result["win_rate"]} ({result["win_rate_amount"]}/{result["tokens_amount"]})')
    print("Released profit: ", result["pnl_released"])
    # print('Unreleased profit: ', result['pnl_unreleased'])
    # pprint(result)
    return result


if __name__ == "__main__":
    universal_page_number = 1
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    now = int(time.time())
    UNTIL_BLOCKNO = get_blockno_by_timestamp(now)
    ROUTE_ADDRESS = "0x81a460ea6fD96a73D5672F1f4aA684697D4B44Cc"

    addrs = set()
    page_number = 1
    route_erc = get_route_history(ROUTE_ADDRESS, page_number)
    ACTIVITY_PERIOD = now - 2 * 24 * 60 * 60  # 2 days from now
    activity_ts = get_blockno_by_timestamp(ACTIVITY_PERIOD)

    for i, tx in enumerate(tqdm(route_erc, f"Parse addresses from {page_number}")):
        if int(tx["timeStamp"]) < int(activity_ts):
            break

        to_contract = check_if_contract(tx["to"])
        if not to_contract:
            addrs.add(tx["to"])
            continue

        from_contract = check_if_contract(tx["from"])
        if not from_contract:
            addrs.add(tx["from"])

        json.dump(list(addrs), open(f"addrs_{ROUTE_ADDRESS[:6]}.json", "w"))

    addrs = list(addrs)[::-1]
    # addrs = ['0xdfd050f52090ccee9734bbdd45e7a76eebe7be6a']
    # addrs = json.load(open('addrs.json', 'r'))[::-1]

    ts_after = now - 7 * 24 * 60 * 60 * 1  # 1 month from now
    TOKEN_HOLDERS_TRESHOLD = 0
    MARKET_CAP_TRESHOLD = 0  # better set to 0 for now

    # if os.path.exists('output.json'):
    #   output = json.load(open('output.json', 'r'))
    # else:
    output = []
    for addr in tqdm(addrs, "Address processing"):
        try:
            result = main(
                addr.lower(),
                ts_after,
                UNTIL_BLOCKNO,
                logger,
                TOKEN_HOLDERS_TRESHOLD,
                MARKET_CAP_TRESHOLD,
            )
            output.append(result)

            # if process_route:
            with open(f"output_{ROUTE_ADDRESS[:6]}.json", "w") as f:
                json.dump(output, f)
        except:
            continue
