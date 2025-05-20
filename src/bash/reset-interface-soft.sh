#!/bin/bash

# Load helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/print.sh"

# Soft reset
bash "$SCRIPT_DIR/set-interface-down.sh" # Down
bash "$SCRIPT_DIR/set-interface-up.sh" # Up