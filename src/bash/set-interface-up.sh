#!/bin/bash

# Load environment
source "$(dirname "${BASH_SOURCE[0]}")/fn_load-env.sh"

# Bring interface up
echo "[INFO] Bringing interface $INTERFACE up..."
sudo ip link set $INTERFACE up
sleep 3