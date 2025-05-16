#!/bin/bash

# Load environment
source "$(dirname "${BASH_SOURCE[0]}")/fn_load-env.sh"

# Set interface down
bash "$SCRIPT_DIR/set-interface-down.sh"

# Bring interface up
bash "$SCRIPT_DIR/set-interface-up.sh"