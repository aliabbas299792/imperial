import argparse

from procedures.generate_proof import generate_proof
from procedures.generate_txs import generate_txs
from procedures.get_tx_hash import get_tx_hash
from procedures.produce_blocks import produce_blocks
from procedures.verify_proof import verify_proof


def main():
    # top-level parser
    parser = argparse.ArgumentParser(description="Blockchain operations tool")
    parser.add_argument(
        "--blockchain-state",
        required=True,
        type=str,
        help="Path to the blockchain state file",
    )

    # subparsers for the positional commands
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # produce-blocks
    parser_produce_blocks = subparsers.add_parser(
        "produce-blocks", help="Produce blocks from the mempool"
    )
    parser_produce_blocks.add_argument(
        "--mempool", required=True, type=str, help="Path to the mempool file"
    )
    parser_produce_blocks.add_argument(
        "--blockchain-output",
        required=True,
        type=str,
        help="Output path for the blockchain",
    )
    parser_produce_blocks.add_argument(
        "--mempool-output", required=True, type=str, help="Output path for the mempool"
    )
    parser_produce_blocks.add_argument(
        "-n", "--number", required=True, type=int, help="Number of blocks to produce"
    )

    # get-tx-hash
    parser_get_tx_hash = subparsers.add_parser(
        "get-tx-hash", help="Get the transaction hash from a block"
    )
    parser_get_tx_hash.add_argument("block_number", type=int, help="Block number")
    parser_get_tx_hash.add_argument(
        "transaction_number", type=int, help="Transaction number"
    )

    # generate-proof
    parser_generate_proof = subparsers.add_parser(
        "generate-proof", help="Generate a proof for a transaction"
    )
    parser_generate_proof.add_argument("block_number", type=int, help="Block number")
    parser_generate_proof.add_argument(
        "transaction_hash", type=str, help="Transaction hash"
    )
    parser_generate_proof.add_argument(
        "-o", "--output", required=True, type=str, help="Output path for the proof"
    )

    # verify-proof
    parser_verify_proof = subparsers.add_parser("verify-proof", help="Verify a proof")
    parser_verify_proof.add_argument(
        "output_path", type=str, help="Path to the proof file"
    )

    # generate-txs
    parser_generate_txs = subparsers.add_parser(
        "generate-txs", help="Generate transactions"
    )
    parser_generate_txs.add_argument(
        "-n",
        "--number",
        required=True,
        type=int,
        help="Number of transactions to generate",
    )
    parser_generate_txs.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        help="Output file for the transactions",
    )
    parser_generate_txs.add_argument(
        "-a", "--accounts", required=True, type=str, help="Path to the accounts file"
    )

    # parse the arguments and load them into variables to use
    args = parser.parse_args()
    blockchain_state = args.blockchain_state

    if args.command == "produce-blocks":
        mempool = args.mempool
        blockchain_output = args.blockchain_output
        mempool_output = args.mempool_output
        number = args.number
        produce_blocks(
            blockchain_state, mempool, blockchain_output, mempool_output, number
        )

    elif args.command == "get-tx-hash":
        block_number = args.block_number
        transaction_number = args.transaction_number
        get_tx_hash(blockchain_state, block_number, transaction_number)

    elif args.command == "generate-proof":
        block_number = args.block_number
        transaction_hash = args.transaction_hash
        output = args.output
        generate_proof(blockchain_state, block_number, transaction_hash, output)

    elif args.command == "verify-proof":
        output_path = args.output_path
        verify_proof(blockchain_state, output_path)

    elif args.command == "generate-txs":
        number = args.number
        output = args.output
        accounts = args.accounts
        generate_txs(blockchain_state, number, output, accounts)


if __name__ == "__main__":
    main()
