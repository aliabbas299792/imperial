from hashlib import sha256
from pathlib import Path
from collections import defaultdict
from utils import save_json_gz, hash_pair
from constants import ZERO_HASH
from models import Blockchain, Mempool, Transaction, Block, Header, HexType


def mine_block(new_block: Block) -> None:
    """
    Mines blocks via Proof-of-Work - adjusting the block's nonce until the
    hash meets the required difficulty level
    Modifies the new block in-place
    """
    new_block.header.nonce = 0
    header_hash = ""
    target_pre = "0" * new_block.header.difficulty

    while not header_hash.startswith(target_pre):
        header_hash = sha256(
            new_block.header.compute_model_hash(fields_to_exclude=["hash"])
        ).hexdigest()
        new_block.header.nonce += 1

    new_block.header.hash = "0x" + header_hash


def construct_merkle_tree_root(transactions: list[Transaction]):
    if not transactions:
        raise ValueError("Cannot generate Merkle root when there's no transactions")

    hashes = [t.compute_model_hash_hex() for t in transactions]
    while len(hashes) > 1:
        next_hashes = []

        if len(hashes) % 2 == 1:
            hashes.append(ZERO_HASH)

        for h1, h2 in zip(hashes[::2], hashes[1::2]):
            next_hashes.append(hash_pair(h1, h2))

        hashes = next_hashes

    return hashes[0]


def execute_transaction(
    tx: Transaction, miner_address: HexType, balances: dict
) -> None:
    """
    Simulating the execution of a transaction
    """
    balances[tx.sender] -= tx.amount + tx.transaction_fee
    balances[tx.receiver] += tx.amount
    balances[miner_address] += tx.transaction_fee


def produce_blocks(
    blockchain: Blockchain,
    mempool: Mempool,
    blockchain_output: Path,
    mempool_output: Path,
    number: int,  # number of blocks to produce
):
    balances = defaultdict(float)

    # build up the balances from the start
    for block in blockchain:
        block: Block
        for tx in block.transactions:
            tx: Transaction
            balances[tx.sender] -= tx.amount + tx.transaction_fee
            balances[tx.receiver] += tx.amount
            balances[block.header.miner] += tx.transaction_fee

    miner_address = block.header.miner  # any miner address is valid for this tutorial
    last_height = block.header.height
    last_hash = block.header.hash
    last_timestamp = block.header.timestamp

    invalid_txs = []
    valid_txs = []
    new_blocks = Blockchain([])

    for tx in mempool:
        if tx.verify_signature():
            valid_txs.append(tx)
        else:
            invalid_txs.append(tx)

    while len(new_blocks) < number:
        next_timestamp = last_timestamp + 10
        next_height = last_height + 1
        next_difficulty = min(6, next_height // 50)  # max difficulty of 6

        # sort the transactions by lock time
        valid_txs.sort(key=lambda tx: tx.lock_time)
        i = 0
        for i, tx in enumerate(valid_txs):
            if tx.lock_time > next_timestamp:
                break
        executable_txs, not_executable_txs = valid_txs[:i], valid_txs[i:]

        # sort the mempool by value
        executable_txs.sort(key=lambda tx: -tx.transaction_fee)
        # take up to 100 transactions for this block
        most_valuable_txs, remaining_txs = executable_txs[:100], executable_txs[100:]
        # we've taken a certain amount from the pool, the rest is still free to use
        valid_txs = remaining_txs + not_executable_txs

        for tx in most_valuable_txs:
            execute_transaction(tx, miner_address, balances)

        merkle_root = construct_merkle_tree_root(most_valuable_txs)

        new_block = Block(
            header=Header(
                height=next_height,
                difficulty=next_difficulty,
                miner=miner_address,
                nonce=0,  # default
                hash=None,  # compute it after this
                previous_block_header_hash=last_hash,
                timestamp=next_timestamp,
                transactions_count=len(most_valuable_txs),
                transactions_merkle_root=merkle_root,
            ),
            transactions=most_valuable_txs,
        )

        # calculate and set the header's hash once it's been computed
        next_hash = new_block.header.compute_model_hash_hex(fields_to_exclude=["hash"])
        new_block.header.hash = next_hash

        # adjust the nonce value until the new block respects the chain difficulty
        mine_block(new_block)

        new_blocks.append(new_block)

        last_height = next_height
        last_hash = next_hash
        last_timestamp = next_timestamp

    # the overall remaining transactions
    remaining_mempool = Mempool(valid_txs + invalid_txs)

    save_json_gz(blockchain_output, new_blocks.model_dump())
    save_json_gz(mempool_output, remaining_mempool.model_dump())
