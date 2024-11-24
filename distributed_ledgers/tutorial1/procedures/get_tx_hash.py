from models import Blockchain


def get_tx_hash(blockchain: Blockchain, block_number: int, transaction_number: int):
    transaction = blockchain[block_number].transactions[transaction_number]
    return transaction.compute_transaction_hash_hex()


def print_tx_hash(blockchain: Blockchain, block_number: int, transaction_number: int):
    print(get_tx_hash(blockchain, block_number, transaction_number))
