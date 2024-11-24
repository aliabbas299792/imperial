import ecdsa
from hashlib import sha256
from pathlib import Path
from collections import defaultdict
from utils import save_json_gz, from_hex
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
        header_hash = sha256(new_block.header.compute_hash(fields_to_exclude=["hash"])).hexdigest()
        new_block.header.nonce += 1
    
    new_block.header.hash = "0x" + header_hash

def hash_pair(a: str, b: str) -> str:
    hash_str = a + b if a < b else b + a
    return "0x" + sha256(hash_str.encode()).hexdigest()

def construct_merkle_tree_root(transactions: list[Transaction]):
    if not transactions:
      raise ValueError("Cannot generate Merkle root when there's no transactions")
    hashes = [t.compute_hash_hex() for t in transactions]
    
    def calc_root(hs):
      if len(hs) == 1:
        return hash_pair(hs[0], ZERO_HASH)
      elif len(hs) == 2:
        return hash_pair(hs[0], hs[1])
      left_hash = calc_root(hs[len(hs) // 2:])
      right_hash = calc_root(hs[:len(hs) // 2])
      return hash_pair(left_hash, right_hash)
    
    return calc_root(hashes)

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
        if True or valid_transaction(tx):
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
    remaining_mempool = Mempool(valid_txs + invalid_txs)

    save_json_gz(blockchain_output, new_blocks.model_dump())
    save_json_gz(mempool_output, remaining_mempool.model_dump())
