#!/bin/bash

# Load environment
source "$(dirname "${BASH_SOURCE[0]}")/fn_load-env.sh"

# Read interface state
LINK_OUTPUT=$(ip link show "$INTERFACE")
STATE=$(echo "$LINK_OUTPUT" | grep "UP")  # Extract UP indicator

# Read interface mode
MODE=$(iw dev "$INTERFACE" info | awk '/type/ {print $2}')

# Display interface
echo "Interface: $INTERFACE"

# Display interface state
if [ -n "$STATE" ]; then
    echo "State: UP"
else
    echo "State: DOWN"
fi

# Display interface mode
if [ -n "$MODE" ]; then
    echo "Mode: $MODE"
else
    echo "[WARN] Could not determine mode for interface $INTERFACE."
fi