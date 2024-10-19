from utils import model_hash
from models import Blockchain


def get_tx_hash(blockchain: Blockchain, block_number: int, transaction_number: int):
    transaction = blockchain[block_number].transactions[transaction_number]
    return model_hash(transaction, fields_to_exclude=["signature"])


def print_tx_hash(blockchain: Blockchain, block_number: int, transaction_number: int):
    print(get_tx_hash(blockchain, block_number, transaction_number))
