#!/bin/bash
# Deploys a contract to the L2 Optimism mainnet via the public Optimism RPC node

set -e
source .env
source utils/common.env

if [[ -z "$PRIVATE_KEY" || -z "$OPTIMISM_RPC_URL" ]]; then
    echo "Error: PRIVATE_KEY and OPTIMISM_RPC_URL must be set in .env"
    exit 1
fi

forge script "$DEPLOY_SCRIPT" \
    --rpc-url "$OPTIMISM_RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --broadcast