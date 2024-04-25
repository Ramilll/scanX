from hmac import new
from db import Database
from aiogram import Bot
from etherscan.client import EtherscanClient
from bot.config import Config
from datetime import datetime

from etherscan.transaction.normal_transaction import NormalTransaction

database = Database()
bot = Bot(token=Config.BOT_TOKEN)
client = EtherscanClient()


async def monitor_addresses():
    addresses = []

    
    with database as db:
        addresses = db.get_subscribed_addresses()
    
    pool: dict[str, list[NormalTransaction]] = {} # address -> transactions
    for address in addresses:
        # can't be parallelized due to rate limits
        # for parallelization must be used Celery or similar
        pool[address] = pool.get(address, []) + await get_new_transactions(address, datetime.now())
    
    notifications: dict[str, dict[str, list[NormalTransaction]]] = {} # user -> address -> transactions    
    with database as db:
        for address, transactions in pool.items():
            users = db.get_subscribers_by_address(address)
            for user in users:
                if user not in notifications:
                    notifications[user] = {}
                notifications[user][address] = transactions

        
    for user, transactions in notifications.items():
        message = "New transactions:\n"
        for address, txs in transactions.items():
            message += f"Address: {address}\n"
            for tx in txs:
                message += f"Hash: <code>{tx.tx_hash}</code>\n"
                message += f"From: <code>{tx.from_address}</code>\n"
                message += f"To: <code>{tx.to_address}</code>\n"
                message += f"Value: <code>{tx.value}</code>\n"
                message += "\n"
            
        await bot.send_message(user, message, parse_mode="HTML")
        

        

async def get_new_transactions(address: str, last_check: datetime) -> list[NormalTransaction]:
    transactions = client.get_normal_transaction_history(address)
    last_check_ts = last_check.timestamp()
    new_transactions: list[NormalTransaction] = []
    for tx in transactions:
        if tx.timestamp > last_check_ts:
            new_transactions.append(tx)
    return new_transactions

    