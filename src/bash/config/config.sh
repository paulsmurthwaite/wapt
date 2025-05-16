# Absolute Path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"  # /src/bash

# Project Root
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"  # /WAPT-Project

# Output Directories
SCN_DIR="$PROJECT_ROOT/src/output/scans"
CAP_DIR="$PROJECT_ROOT/src/output/captures"

# File naming convention
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
FILE_BASE="$TIMESTAMP"

# WLAN Parameters
CHANNELS_24GHZ_UK="1,2,3,4,5,6,7,8,9,10,11,12,13"
CHANNELS_5GHZ_UK="36,40,44,48"
INTERFACE="wlp3s0"

# Recommended durations and packet counts
DEFAULT_SCAN_DURATION=30
DEFAULT_CAPTURE_DURATION=60
DEFAULT_CAPTURE_PACKETS=500
DEFAULT_FILTERED_CAPTURE_DURATION=30
DEFAULT_FILTERED_CAPTURE_PACKETS=300