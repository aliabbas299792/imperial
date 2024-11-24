# Tutorial 1
This implements some of the core functionality of a simple blockchain in Python.
It was designed to mimic the interface in the examples of the tutorial.
## Examples
### Block Production
Produce 15 blocks, reading the state from `./data/blockchain.json.gz`, the mempool from `./data/mempool.json.gz`, writing the new state to `new-blockchain.json.gz` and the new mempool to `new-mempool.json.gz`
```shell
python blockchain_poc.py \
    --blockchain-state data/blockchain.json.gz \
    produce-blocks \
    --mempool data/mempool.json.gz \
    --blockchain-output new_bc.json.gz \
    --mempool-output new_mp.json.gz \
    -n 10
```
### Getting Transaction Hashes
Get the hash of the 7th transaction in block 18
```shell
python blockchain_poc.py \
    --blockchain-state ./data/blockchain.json.gz\
    get-tx-hash 18 7
```
### Getting Inclusion Proofs
Generate the inclusion proof for the 7th transaction in block 18 (using the hash retrieved above), and save it to `proof.json`
```shell
python blockchain_poc.py \
    --blockchain-state ./data/blockchain.json.gz \
    generate-proof 18 0x20f9ca5187d9789d983d238f9e80aba6a8fb2cebd0fa775e075fe79c006b6455 \
    -o proof.json
```
### Verifying Inclusion Proofs
Verify the inclusion proof saved in `proof.json`
```shell
python blockchain_poc.py \
    --blockchain-state ./data/blockchain.json.gz \
    verify-proof proof.json
```
### Generate New Transactions
Generate 2000 new transactions using accounts in `data/keys.json.gz` and save them to `new-mempool.json.gz`
```shell
python blockchain_poc.py \
    --blockchain-state ./data/blockchain.json.gz \
    generate-txs \
    -n 2000 \
    -o new-mempool.json.gz \
    -a data/keys.json.gz
```
