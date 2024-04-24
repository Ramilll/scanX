class BaseTransaction:
    def __init__(self, transaction: dict) -> None:
        """
        base class for all transactions
        """
        self.transaction_name = "base_transaction"
        self.block_number = int(transaction["blockNumber"])
        self.timestamp = int(transaction["timeStamp"])
        self.from_address = transaction["from"].lower()
        self.contract_address = transaction["contractAddress"].lower()
        self.to_address = transaction["to"].lower()
        self.tx_hash = transaction["hash"].lower()
        self.gas = int(transaction["gas"])
        self.gas_used = int(transaction["gasUsed"])
        self.input_data = transaction["input"]
        self.value = int(transaction["value"])

    def __repr__(self):
        class_name = self.__class__.__name__
        _repr = class_name + ": {"
        for param in self.__dict__:
            _repr += f"{param}: {self.__dict__[param]},\n"
        return _repr + "}\n"

    def params(self):
        return list(self.__dict__.keys())
