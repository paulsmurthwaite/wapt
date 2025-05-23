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

# Read interface state
LINK_OUTPUT=$(ip link show "$INTERFACE")
STATE=$(echo "$LINK_OUTPUT" | grep "UP")  # Extract UP indicator

# Read interface mode
MODE=$(iw dev "$INTERFACE" info | awk '/type/ {print $2}')

# Display interface
print_none "Interface: $INTERFACE"

# Display interface state
if [ -n "$STATE" ]; then
    print_none "State: UP"
else
    print_none "State: DOWN"
fi

# Display interface mode
if [ -n "$MODE" ]; then
    print_none "Mode: $MODE"
else
    print_warn "[WARN] Could not determine mode for interface $INTERFACE."
fi