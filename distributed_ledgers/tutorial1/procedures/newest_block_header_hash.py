from models import Blockchain


def newest_block_header_hash(blockchain: Blockchain):
    newest_block = len(blockchain) - 1
    print(hex(blockchain[newest_block].header.hash))
