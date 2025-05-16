#!/bin/bash

# Load environment
source "$(dirname "${BASH_SOURCE[0]}")/fn_load-env.sh"

# Change mode
bash "$SCRIPT_DIR/set-interface-down.sh"  # Interface down
echo "[INFO] Setting Monitor mode on interface $INTERFACE ..."
sudo iw dev $INTERFACE set type monitor
bash "$SCRIPT_DIR/set-interface-up.sh"  # Interface up