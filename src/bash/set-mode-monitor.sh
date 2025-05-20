#!/bin/bash

# Load helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/print.sh"

# Change mode
bash "$SCRIPT_DIR/set-interface-down.sh"  # Interface down
print_action "Setting interface mode MONITOR"
sudo iw dev $INTERFACE set type monitor
bash "$SCRIPT_DIR/set-interface-up.sh"  # Interface up