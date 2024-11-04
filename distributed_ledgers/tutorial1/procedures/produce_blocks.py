import ecdsa
from pathlib import Path
from collections import defaultdict
from utils import save_json_gz, from_hex
from models import Blockchain, Mempool, Transaction, Block, Header, HexType


def mine_block(new_block: Block):
    """
    TODO: implement the proof of work algorithm
    """


def construct_merkle_tree_root(transactions: list[Transaction]):
    """
    TODO: add code to construct the merkle tree root
    """


def valid_transaction(tx: Transaction) -> bool:
    try:
        der_hex_pub_key, hex_signed_hash = tx.signature.split(",")
        computed_hash = tx.compute_hash(fields_to_exclude=["signature"])
        pub_key = ecdsa.VerifyingKey.from_der(from_hex(der_hex_pub_key))
        return pub_key.verify_digest(
            from_hex(hex_signed_hash),
            computed_hash,
            sigdecode=ecdsa.util.sigdecode_der,
        )
    except ecdsa.BadSignatureError:
        return False  # invalid transaction if anything failed


def execute_transaction(
    tx: Transaction, miner_address: HexType, balances: dict
) -> None:
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
        if valid_transaction(tx):
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
        next_hash = new_block.header.compute_hash_hex(fields_to_exclude=["hash"])
        new_block.header.hash = next_hash

        # adjust the nonce value until the new block respects the chain difficulty
        mine_block(new_block)

        new_blocks.append(new_block)

        last_height = next_height
        last_hash = next_hash
        last_timestamp = next_timestamp

    # the overall remaining transactions
    print(f"There are {len(invalid_txs)} invalid transactions in the mempool")
    remaining_mempool = Mempool(valid_txs + invalid_txs)

    save_json_gz(blockchain_output, new_blocks.model_dump())
    save_json_gz(mempool_output, remaining_mempool.model_dump())
