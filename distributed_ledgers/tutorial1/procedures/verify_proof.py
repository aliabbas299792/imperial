from models import Blockchain, BlockInclusionProof
from utils import hash_pair


def verify_proof(blockchain: Blockchain, proof: BlockInclusionProof) -> bool:
    """
    Verifies a given proof against the blockchain
    """

    if proof.block_number < 0 or proof.block_number >= len(blockchain):
        return False

    block_merkle_root = blockchain[proof.block_number].header.transactions_merkle_root
    computed_hash = proof.transaction_hash

    for sibling_hash in proof.proof:
        computed_hash = hash_pair(computed_hash, sibling_hash)

    is_valid = computed_hash == block_merkle_root == proof.merkle_root
    print(f"Proof is valid: {is_valid}")
