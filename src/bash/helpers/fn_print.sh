#!/bin/bash

# ─── Standardise Output Formatting ───

print_section() {
    echo -e "\033[1m[ $1 ]\033[0m"
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

print_none() {
    echo "$1"
}

print_blank() {
    echo ""
}