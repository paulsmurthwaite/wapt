#!/bin/bash

LEASE_FILE="/var/lib/misc/dnsmasq.leases"

# Check if the lease file exists and is not empty
if [ -f "$LEASE_FILE" ] && [ -s "$LEASE_FILE" ]; then
    # The file exists and has content, display it
    sudo cat "$LEASE_FILE"
else
    # The file does not exist or is empty
    echo "No active or previous DHCP leases found."
fi
