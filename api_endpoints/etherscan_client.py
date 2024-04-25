import requests
from utils.config import Config


class EtherscanClient:
    BASE_URL = Config.ETHERSCAN_API_URL

    def __init__(self, api_key=Config.ETHERSCAN_API_KEY):
        self.api_key = api_key
        self.session = requests.Session()

    def _get(self, params):
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        result = response.json()
        if result["status"] == "0":
            if result["message"] == "No transactions found":
                return []
            raise Exception(result["message"])
        return result["result"]

    def get_normal_transaction_history(
        self, address, start_block=0, end_block=99999999, page=1, offset=-1, sort="asc"
    ):
        """
        Returns the list of transactions performed by an address, with optional pagination.
        """

        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": offset,
            "sort": sort,
            "apikey": self.api_key,
        }
        return self._get(params)

    def get_erc20_transaction_history(
        self, address, start_block=0, end_block=99999999, page=1, offset=-1, sort="asc"
    ):
        """
        Returns the list of ERC-20 tokens transferred by an address, with optional filtering by token contract
        """

        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": offset,
            "sort": sort,
            "apikey": self.api_key,
        }
        return self._get(params)

    def get_internal_transaction_history(
        self, address, start_block=0, end_block=99999999, page=1, offset=-1, sort="asc"
    ):
        """
        Returns the list of internal transactions performed by an address, with optional pagination.
        """

        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": offset,
            "sort": sort,
            "apikey": self.api_key,
        }
        return self._get(params)

    def get_token_info(self, contract_address):
        "Returns project information and social media links of an ERC20/ERC721/ERC1155 token."
        params = {
            "module": "token",
            "action": "tokeninfo",
            "contractaddress": contract_address,
            "apikey": self.api_key,
        }
        return self._get(params)
