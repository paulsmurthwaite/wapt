#!/bin/bash

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Set interface down
echo "[INFO] Bringing interface $INTERFACE down..."
sudo ip link set $INTERFACE down
sudo ip addr flush dev "$INTERFACE"
sleep 3