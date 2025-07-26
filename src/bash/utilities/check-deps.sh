#!/bin/bash
#
# check-deps.sh
#
# Checks if required command-line utilities are installed and available in the PATH.
# Exits with a non-zero status code if any dependency is missing.
#
# Usage: ./check-deps.sh <dep1> <dep2> ...

# Use a flag to track if any dependency is missing
missing_deps=0

# Check if at least one dependency is provided
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <dependency1> <dependency2> ..." >&2
    exit 1
fi

# Loop through all provided arguments (dependencies)
for dep in "$@"; do
    # 'command -v' is a portable way to check if a command exists
    if ! command -v "$dep" &> /dev/null; then
        # Print error to stderr so the calling script can capture it
        echo "Error: Required dependency '$dep' is not installed or not in PATH." >&2
        missing_deps=1
    fi
done

exit "$missing_deps"