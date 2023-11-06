import requests
import json
from config import *

def fetch_all_transactions(contract_address, page_start=1, page_end = 100, start_block=0, end_block=99999999, offset=100):
    all_transactions = []

    while page_start <= page_end:
        url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={contract_address}&startblock={start_block}&endblock={end_block}&page={page_start}&offset={offset}&sort=asc&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url)
        data = json.loads(response.text)

        transactions = data.get("result")

        if not transactions:
            # No more transactions, break the loop
            break

        all_transactions.extend(transactions)
        
        # Go to next page
        page_start += 1

    return all_transactions

