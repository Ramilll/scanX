from celery import Celery
from celery.schedules import crontab
from loguru import logger
from api_endpoints.etherscan_client import EtherscanClient
from bot.config import Config
import requests
from db import (
    Database,
    Address,
    EtherscanNormalTransaction,
    EtherscanERC20Transaction,
    EtherscanInternalTransaction,
)

app = Celery(
    "worker",
    broker=f"amqp://{Config.RABBITMQ_USER}:{Config.RABBITMQ_PASSWORD}@{Config.RABBITMQ_HOST}:5672",
    result_backend="rpc://",
    broker_connection_retry_on_startup=True,
)
client = EtherscanClient()
app.conf.beat_schedule = {
    "refill_pool_every_hour": {
        "task": "worker.refill_pool",
        # every 20 seconds
        "schedule": crontab(minute="*/1"),
    },
}

print("Worker started")
database = Database()


def process_normal_transactions(transactions: list[EtherscanNormalTransaction]):
    amount = 0
    with database as db:
        for tx in transactions:
            db.add_normal_transaction(tx)
            db.add_address(tx.from_address)
            db.add_address(tx.to_address)
            amount += 1
        db.session.commit()
    return amount


def process_erc20_transactions(transactions: list[EtherscanERC20Transaction]):
    amount = 0
    with database as db:
        for tx in transactions:
            db.add_erc20_transaction(tx)
            db.add_address(tx.from_address)
            db.add_address(tx.to_address)
            amount += 1
        db.session.commit()
    return amount


def process_internal_transactions(transactions: list[EtherscanInternalTransaction]):
    amount = 0
    with database as db:
        for tx in transactions:
            db.add_internal_transaction(tx)
            db.add_address(tx.from_address)
            db.add_address(tx.to_address)
            amount += 1
        db.session.commit()
    return amount


@app.task(
    name="parser.process_address",
    retry_backoff=True,
    max_retries=3,
    queue="parser",
    rate_limit="250/m",
    time_limit=60, # 1 minute
)
def process_address(address):
    with database as db:
        if db.is_address_processed(address):
            return
    try:
        normal_transactions = client.get_normal_transaction_history(address)
        erc20_transactions = client.get_erc20_transaction_history(address)
        internal_transactions = client.get_internal_transaction_history(address)
    except Exception as e:
        logger.error(f"Error processing {address}: {e}")
        with database as db:
            db.mark_address_as_processed(address)
            db.session.commit()
        return

    normal_amount = process_normal_transactions(normal_transactions)
    erc20_amount = process_erc20_transactions(erc20_transactions)
    internal_amount = process_internal_transactions(internal_transactions)
    logger.info(f"Processed {address}")
    with database as db:
        db.mark_address_as_processed(address)
        db.session.commit()
    return {
        "address": address,
        "normal_transactions": normal_amount,
        "erc20_transactions": erc20_amount,
        "internal_transactions": internal_amount,
    }


def get_queue_size(queue_name: str):
    response = requests.get(
        f"http://root:root@{Config.RABBITMQ_HOST}:15672/api/queues/%2F/{queue_name}"
    )
    data = response.json()
    return data["messages"]


@app.task(name="worker.refill_pool", queue="worker")
def refill_pool():
    extra = 100 - get_queue_size("parser")
    if extra <= 0:
        return {
            "amount": 0,
            "message": "Queue is full, no need to refill",
        }
    with database as db:
        addresses = (
            db.session.query(Address).filter_by(processed=False).limit(extra).all()
        )
        amount = len(addresses)
        for address in addresses:
            process_address.apply_async(args=(str(address.address),), queue="parser")
    return {
        "amount": amount,
    }
