#!/bin/bash
# Usage:
# ./stop-ap.sh

set -e

IFACE="wlx00c0cab4b58c"

# Stop hostapd
echo "{+] Stopping hostapd ... "
sudo pkill hostapd
rm -f /tmp/watt_ap_active

# Stop dnsmasq
echo "{+] Stopping dnsmasq ... "
sudo pkill dnsmasq

# Restore systemd-resolved
echo "{+] Restoring systemd-resolved ... "
sudo systemctl start systemd-resolved

# Relink /etc/resolv.conf
echo "{+] Relinking /etc/resolv.conf ... "
sudo rm -f /etc/resolv.conf
sudo ln -s /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# Flush iptables
echo "{+] Flushing iptables ... "
sudo iptables -F
sudo iptables -t nat -F

# Disable IP Forwarding
echo 0 | sudo tee /proc/sys/net/ipv4/ip_forward > /dev/null

# Reset Wi-Fi Interface
echo "{+] Resetting interface $IFACE ... "
sudo ip link set $IFACE down
sudo ip addr flush dev $IFACE
sudo ip link set $IFACE up

# Reenable NetworkManager
echo "{+] Starting NetworkManager ... "
sudo systemctl start NetworkManager

echo "{+] AP DISABLED ... "