#!/bin/bash
# Deploys a contract to the local fork

set -e
source .env

if [[ -z "$ETH_RPC_URL" || -z "$PRIVATE_KEY" || -z "$DEPLOY_SCRIPT" ]]; then
    echo "Error: ETH_RPC_URL, PRIVATE_KEY and DEPLOY_SCRIPT must be set in .env"
    exit 1
fi

forge build

forge_out=$(forge script "$DEPLOY_SCRIPT" \
    --rpc-url "$ETH_RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --broadcast)

replacement=$(echo $forge_out | sed -n "s/^.*Deployed at: \(0x[A-Za-z0-9]*\).*/\1/p")

sed -i "" "s/HR_CONTRACT=0x.*/HR_CONTRACT=$replacement/" "./.env"
