#!/bin/bash

# Load environment
source "$(dirname "${BASH_SOURCE[0]}")/fn_load-env.sh"

# Set interface down
echo "[INFO] Bringing interface $INTERFACE down..."
sudo ip link set $INTERFACE down
sleep 3