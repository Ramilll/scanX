from sqlalchemy import Boolean, create_engine, Column, String, BigInteger
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from transaction.normal_transaction import (
    NormalTransaction as EtherscanNormalTransaction,
)
from transaction.erc20_transaction import (
    ERC20Transaction as EtherscanERC20Transaction,
)
from transaction.internal_transaction import (
    InternalTransaction as EtherscanInternalTransaction,
)

Base = declarative_base()


class NormalTransaction(Base):
    __tablename__ = "normal_transactions"
    tx_hash = Column(String, primary_key=True)
    block_number = Column(String)
    timestamp = Column(BigInteger)
    from_address = Column(String)
    to_address = Column(String)
    contract_address = Column(String)
    gas = Column(String)
    gas_used = Column(String)
    input_data = Column(String)
    value = Column(String)
    block_hash = Column(String)
    method_id = Column(String)
    function_name = Column(String)
    cumulative_gas_used = Column(String)
    gas_price = Column(String)
    is_error = Column(String)
    nonce = Column(String)
    confirmations = Column(String)
    transaction_index = Column(String)
    tx_receipt_status = Column(String)

    @classmethod
    def from_etherscan(cls, tx: EtherscanNormalTransaction):
        return cls(
            tx_hash=tx.tx_hash,
            block_number=str(tx.block_number),
            timestamp=tx.timestamp,
            from_address=tx.from_address,
            to_address=tx.to_address,
            contract_address=tx.contract_address,
            gas=str(tx.gas),
            gas_used=str(tx.gas_used),
            input_data=tx.input_data,
            value=str(tx.value),
            block_hash=tx.block_hash,
            method_id=tx.method_id,
            function_name=tx.function_name,
            cumulative_gas_used=str(tx.cumulative_gas_used),
            gas_price=str(tx.gas_price),
            is_error=str(tx._is_error),
            nonce=str(tx.nonce),
            confirmations=str(tx.confirmations),
            transaction_index=str(tx.transaction_index),
            tx_receipt_status=str(tx.tx_receipt_status),
        )


class ERC20Transaction(Base):
    __tablename__ = "erc20_transactions"
    tx_hash = Column(String, primary_key=True)
    block_number = Column(String)
    timestamp = Column(BigInteger)
    from_address = Column(String)
    to_address = Column(String)
    contract_address = Column(String)
    gas = Column(String)
    gas_used = Column(String)
    input_data = Column(String)
    value = Column(String)
    block_hash = Column(String)
    token_name = Column(String)
    token_symbol = Column(String)
    cumulative_gas_used = Column(String)
    gas_price = Column(String)
    token_decimal = Column(String)
    nonce = Column(String)
    confirmations = Column(String)
    transaction_index = Column(String)

    @classmethod
    def from_etherscan(cls, tx: EtherscanERC20Transaction):
        return cls(
            tx_hash=tx.tx_hash,
            block_number=str(tx.block_number),
            timestamp=tx.timestamp,
            from_address=tx.from_address,
            to_address=tx.to_address,
            contract_address=tx.contract_address,
            gas=str(tx.gas),
            gas_used=str(tx.gas_used),
            input_data=tx.input_data,
            value=str(tx.value),
            block_hash=tx.block_hash,
            token_name=tx.token_name,
            token_symbol=tx.token_symbol,
            cumulative_gas_used=str(tx.cumulative_gas_used),
            gas_price=str(tx.gas_price),
            token_decimal=str(tx.token_decimal),
            nonce=str(tx.nonce),
            confirmations=str(tx.confirmations),
            transaction_index=str(tx.transaction_index),
        )


class InternalTransaction(Base):
    __tablename__ = "internal_transactions"
    tx_hash = Column(String, primary_key=True)
    block_number = Column(String)
    timestamp = Column(BigInteger)
    from_address = Column(String)
    to_address = Column(String)
    contract_address = Column(String)
    gas = Column(String)
    gas_used = Column(String)
    input_data = Column(String)
    value = Column(String)
    is_error = Column(String)
    error_code = Column(String)
    trace_id = Column(String)
    type = Column(String)

    @classmethod
    def from_etherscan(cls, tx: EtherscanInternalTransaction):
        return cls(
            tx_hash=tx.tx_hash,
            block_number=str(tx.block_number),
            timestamp=tx.timestamp,
            from_address=tx.from_address,
            to_address=tx.to_address,
            contract_address=tx.contract_address,
            gas=str(tx.gas),
            gas_used=str(tx.gas_used),
            input_data=tx.input_data,
            value=str(tx.value),
            is_error=str(tx.is_error),
            error_code=str(tx.err_code),
            trace_id=str(tx.trace_id),
            type=str(tx.type),
        )


class Address(Base):
    __tablename__ = "addresses"
    address = Column(String, primary_key=True)
    processed = Column(Boolean, default=False)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(BigInteger, primary_key=True)
    address = Column(String)
    user_id = Column(String)


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(f"postgresql+psycopg2://dev:dev@localhost:5432/dev")
        Base.metadata.create_all(self.engine)
        self.session: Session
        self.is_open = False

    @staticmethod
    def check_open(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_open:
                raise Exception("Database is not open")
            return func(self, *args, **kwargs)

        return wrapper

    @check_open
    def add_normal_transaction(self, tx: EtherscanNormalTransaction):
        if self.session.query(NormalTransaction).filter_by(tx_hash=tx.tx_hash).first():
            return
        self.session.add(NormalTransaction.from_etherscan(tx))

    @check_open
    def add_erc20_transaction(self, tx: EtherscanERC20Transaction):
        if self.session.query(ERC20Transaction).filter_by(tx_hash=tx.tx_hash).first():
            return
        self.session.add(ERC20Transaction.from_etherscan(tx))

    @check_open
    def add_internal_transaction(self, tx: EtherscanInternalTransaction):
        if (
            self.session.query(InternalTransaction)
            .filter_by(tx_hash=tx.tx_hash)
            .first()
        ):
            return
        self.session.add(InternalTransaction.from_etherscan(tx))

    @check_open
    def get_normal_transactions(self):
        return self.session.query(NormalTransaction).all()

    @check_open
    def get_erc20_transactions(self):
        return self.session.query(ERC20Transaction).all()

    @check_open
    def get_internal_transactions(self):
        return self.session.query(InternalTransaction).all()

    @check_open
    def add_address(self, address: str):
        if self.session.query(Address).filter_by(address=address).first():
            return
        self.session.add(Address(address=address))

    @check_open
    def is_address_processed(self, address: str) -> bool:
        db_address = self.session.query(Address).filter_by(address=address).first()
        if db_address:
            return bool(db_address.processed)
        return False

    @check_open
    def mark_address_as_processed(self, address: str):
        db_address = self.session.query(Address).filter_by(address=address).first()
        if db_address:
            db_address.processed = True  # type: ignore
        else:
            self.session.add(Address(address=address, processed=True))

    @check_open
    def add_subscription(self, address: str, user_id: str):
        self.session.add(Subscription(address=address, user_id=user_id))

    @check_open
    def get_subscriptions(self) -> list[Subscription]:
        return self.session.query(Subscription).all()

    @check_open
    def get_subscriptions_by_user_id(self, user_id: str) -> list[Subscription]:
        return self.session.query(Subscription).filter_by(user_id=user_id).all()

    @check_open
    def get_subscriptions_by_address(self, address: str) -> list[Subscription]:
        return self.session.query(Subscription).filter_by(address=address).all()

    @check_open
    def get_subscribers_by_address(self, address: str) -> list[str]:
        query = self.session.query(Subscription.user_id).filter_by(address=address).all()
        return [user_id for user_id, in query]

    @check_open
    def remove_subscription(self, address: str, user_id: str):
        self.session.query(Subscription).filter_by(
            address=address, user_id=user_id
        ).delete()

    @check_open
    def is_subscribed(self, address: str, user_id: str) -> bool:
        return bool(
            self.session.query(Subscription)
            .filter_by(address=address, user_id=user_id)
            .first()
        )

    @check_open
    def get_subscribed_addresses(self) -> list[str]:
        query = (
            self.session.query(Subscription.address)
            .group_by(Subscription.address)
            .all()
        )
        return [address for address, in query] 

    def __enter__(self):
        self.session = sessionmaker(bind=self.engine)()
        self.is_open = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.rollback()  # Rollback any uncommitted changes
        self.session.close()
        self.is_open = False
