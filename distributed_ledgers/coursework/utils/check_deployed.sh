#!/bin/bash
# Retrieves the compiled bytecode of a contract, so can implicitly check if it's been deployed

set -e
source .env

if [[ -z "$1" ]]; then
    echo "Usage: ./check_contract.sh <contract-address>"
    exit 1
fi

CONTRACT_ADDRESS=$1

curl -X POST -H "Content-Type: application/json" --data '{
    "jsonrpc":"2.0",
    "method":"eth_getCode",
    "params":["'"$CONTRACT_ADDRESS"'", "latest"],
    "id":1
}' "$OPTIMISM_RPC_URL" | jq
