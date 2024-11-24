from pathlib import Path
from models import BlockInclusionProof, Blockchain, HexType
from constants import ZERO_HASH, JSON_DUMP_INDENT
from utils import hash_pair, enumerated_pair_iter


def generate_proof(
    blockchain: Blockchain, block_number: int, transaction_hash: HexType, output: Path
):
    if block_number < 0 or block_number >= len(blockchain):
        raise ValueError("Invalid block number")

    proof = []
    hashes = [t.compute_model_hash_hex() for t in blockchain[block_number].transactions]
    transaction_idx = hashes.index(transaction_hash)
    tracking_idx = transaction_idx

    while len(hashes) > 1:
        next_hashes = []

        if len(hashes) % 2 == 1:
            hashes.append(ZERO_HASH)

        for idxs, (h1, h2) in enumerated_pair_iter(hashes):
            next_hashes.append(hash_pair(h1, h2))

            if tracking_idx in idxs:
                sibling_idx = idxs[0] if tracking_idx == idxs[1] else idxs[1]
                proof.append(hashes[sibling_idx])
                tracking_idx //= 2

        hashes = next_hashes

    proof_data = BlockInclusionProof(
        block_number=block_number,
        transaction_hash=transaction_hash,
        proof=proof,
        merkle_root=hashes[0],
    )

    output.write_text(proof_data.model_dump_json(indent=JSON_DUMP_INDENT))
