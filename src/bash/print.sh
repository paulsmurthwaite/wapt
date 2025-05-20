#!/bin/bash
#
# Standardised Output Formatting

print_blank() {
    echo ""
}

print_info() {
    echo "[*] $1"
}

print_success() {
    echo "[+] $1"
}

print_fail() {
    echo "[x] $1"
}

print_warn() {
    echo "[!] $1"
}

print_action() {
    echo "[>] $1"
}

print_waiting() {
    echo "[~] $1"
}

print_prompt() {
    echo -n "[?] $1"
}
