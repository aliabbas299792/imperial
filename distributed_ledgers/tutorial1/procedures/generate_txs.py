import ecdsa
from pathlib import Path
from models import Blockchain, Accounts, Transaction
from utils import save_json_gz
import random
from collections import defaultdict


def calculate_balances(blockchain: Blockchain):
    balances = defaultdict(float)

    for block in blockchain:
        for tx in block.transactions:
            balances[tx.sender] -= tx.amount + tx.transaction_fee
            balances[tx.receiver] += tx.amount
            balances[block.header.miner] += tx.transaction_fee

    return balances


def generate_txs(blockchain: Blockchain, number: int, output: Path, accounts: Accounts):
    transactions = []
    balances = calculate_balances(blockchain)
    addresses = list(accounts.keys())

    for _ in range(number):
        sender = random.choice(addresses)
        receiver = random.choice(addresses)

        if sender == receiver:
            continue

        transaction_fee = random.randint(1, 10)

        # skip if the can't afford the fee
        if transaction_fee >= balances.get(sender, 0):
            continue

        # calculate the amount, ensuring sender can afford it
        max_amount = balances[sender] - transaction_fee
        if max_amount <= 0:
            continue
        amount = random.randint(1, int(max_amount))

        tx = Transaction(
            amount=amount,
            lock_time=blockchain[-1].header.timestamp
            + random.randint(0, 3600),  # future lock time
            receiver=receiver,
            sender=sender,
            transaction_fee=transaction_fee,
            signature=None,  # set afterwards
        )

        private_key = accounts.get_as_private_key(sender)
        tx.sign(private_key)

        # update balances locally
        balances[sender] -= amount + transaction_fee
        balances[receiver] += amount

        # append to the transaction list
        transactions.append(tx)

    save_json_gz(output, [tx.model_dump() for tx in transactions])
