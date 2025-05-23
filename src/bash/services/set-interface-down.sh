#!/bin/bash

# ─── Paths ───
BASH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_DIR="$BASH_DIR/config"
HELPERS_DIR="$BASH_DIR/helpers"
SERVICES_DIR="$BASH_DIR/services"

# ─── Configs ───
source "$CONFIG_DIR/global.conf"

# ─── Helpers ───
source "$HELPERS_DIR/fn_print.sh"

# Set interface down
print_action "Setting interface DOWN"
sudo ip link set $INTERFACE down
sudo ip addr flush dev "$INTERFACE"
HWADDR=$(ethtool -P "$INTERFACE" | awk '{print $3}')
sudo ip link set "$INTERFACE" address "$HWADDR"
sleep 3