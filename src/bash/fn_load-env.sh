#!/bin/bash

# Define path to bash/ directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load configuration and helpers
source "$SCRIPT_DIR/config/config.sh"
source "$SCRIPT_DIR/helpers/fn_validate-input.sh"