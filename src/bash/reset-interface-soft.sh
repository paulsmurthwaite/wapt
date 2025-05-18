#!/bin/bash

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Set interface down
bash "$SCRIPT_DIR/set-interface-down.sh"

# Bring interface up
bash "$SCRIPT_DIR/set-interface-up.sh"