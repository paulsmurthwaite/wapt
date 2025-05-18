# Absolute path to /src/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project root
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Interface Configuration
INTERFACE="wlp3s0"
GATEWAY="10.0.0.1"
