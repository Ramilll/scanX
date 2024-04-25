from dataclasses import dataclass

from sqlalchemy import func, desc
from db import Address, NormalTransaction, Database
from transaction.swap_transaction_analyzer import SWAP_FUNCTION_NAMES

database = Database()


@dataclass
class AddressMetric:
    address: str
    metric: float

    def __str__(self):
        return f"{self.address}: {self.metric}"


def get_top_addresses(top: int = 50) -> list[AddressMetric]:
    with database as db:
        query = (
            db.session.query(
                NormalTransaction.from_address,
                NormalTransaction.function_name,
                func.count().label("address_count"),
            )
            .filter(NormalTransaction.function_name.in_(SWAP_FUNCTION_NAMES))
            .group_by(NormalTransaction.from_address, NormalTransaction.function_name)
            .order_by(desc("address_count"))
            .limit(top)
        )

        return [
            AddressMetric(address=address, metric=metric)
            for address, _, metric in query.all()
        ]


if __name__ == "__main__":
    top = get_top_addresses()
    for address in top:
        print(address)
