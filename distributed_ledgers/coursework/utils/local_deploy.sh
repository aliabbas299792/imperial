#!/bin/bash
# Deploys a contract to the local fork

set -e
source .env
source utils/common.env

if [[ -z "$ETH_RPC_URL" || -z "$PRIVATE_KEY" ]]; then
    echo "Error: ETH_RPC_URL and PRIVATE_KEY must be set in .env"
    exit 1
fi

if [[ -z "$DEPLOY_CONTRACT_PATH" || -z "$DEPLOY_CONTRACT_NAME" ]]; then
    echo "Error: DEPLOY_CONTRACT_PATH and DEPLOY_CONTRACT_NAME must be set in utils/common.env"
    exit 1
fi

forge script "$DEPLOY_SCRIPT" \
    --rpc-url "$ETH_RPC_URL" \
    --private-key "$PRIVATE_KEY" \
    --broadcast
