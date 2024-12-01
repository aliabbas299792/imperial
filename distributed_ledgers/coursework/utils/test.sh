#!/bin/bash
# Runs tests locally using a fork of the Optimism mainnet

set -e
source .env

if [[ -z "$ETH_RPC_URL" ]]; then
    echo "Error: ETH_RPC_URL must be set in .env"
    exit 1
fi

forge test --fork-url "$ETH_RPC_URL" -vvv
