#!/bin/bash
# Retrieves the account of a contract

set -e
source .env

if [[ -z "$1" ]]; then
    echo "Usage: ./get_balance.sh <contract-address>"
    exit 1
fi

CONTRACT_ADDRESS=$1

curl -X POST -H "Content-Type: application/json" --data '{
    "jsonrpc":"2.0",
    "method":"eth_getBalance",
    "params":["'"$CONTRACT_ADDRESS"'", "latest"],
    "id":1
}' "$OPTIMISM_RPC_URL" | jq