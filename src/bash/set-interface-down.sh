#!/bin/bash

# Load helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/print.sh"

# Set interface down
print_action "Setting interface DOWN"
sudo ip link set $INTERFACE down
sudo ip addr flush dev "$INTERFACE"
HWADDR=$(ethtool -P "$INTERFACE" | awk '{print $3}')
sudo ip link set "$INTERFACE" address "$HWADDR"
sleep 3