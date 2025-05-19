#!/usr/bin/env python3
"""watt.py

Main entry point for the Wireless Attack Testing Toolkit (WATT) menu interface.

This script provides a simple, operator-friendly CLI for accessing key toolkit functions such as scanning, capturing, and detection.  It is designed to offer a clear and low-complexity user experience, suitable for field use in SME environments.

The menu system acts as the central launcher for Bash and Python-based components of the toolkit, with screen clearing and section redrawing used to improve usability without introducing graphical complexity.

Author:      Paul Smurthwaite
Date:        2025-05-16
Module:      TM470-25B
"""

import pyfiglet
import os
import re
import subprocess
import time

def get_interface_details():
    """
    Returns (interface, state, mode) from get-current-interface.sh.
    """
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bash", "get-current-interface.sh")
    )

    if not os.path.exists(script_path):
        return ("[!] Not found", "[!] Not found", "[!] Not found")

    try:
        result = subprocess.run(["bash", script_path], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        interface = lines[0].split(":")[1].strip().upper() if len(lines) > 0 else "?"
        state     = lines[1].split(":")[1].strip().upper() if len(lines) > 1 else "?"
        mode      = lines[2].split(":")[1].strip().upper() if len(lines) > 2 else "?"
        return (interface, state, mode)
    except subprocess.CalledProcessError:
        return ("[!] Script error", "[!] Script error", "[!] Script error")

def get_current_interface():
    return get_interface_details()[0]

def get_interface_state():
    return f"State:     {get_interface_details()[1]}"

def get_interface_mode():
    return f"Mode:      {get_interface_details()[2]}"

def pause_on_invalid():
    """Display invalid input message and pause."""
    print("\33[91m\n  [!] Invalid option. Please try again.\033[0m")
    input("  [Press Enter to continue]")

def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title="Wireless Access Point Toolkit"):
    """Print section header."""
    print(f"\033[1;93m[ {title} ]\033[0m")

def print_divider():
    print("\033[90m-----------------------------------\033[0m")
    print()

def print_interface_status():
    """Print the current interface, state, and mode."""
    interface, state_raw, mode_raw = get_interface_details()

    state = state_raw.title()
    mode = "AP" if mode_raw.lower() == "ap" else mode_raw.title()

    interface_colour = "\033[38;5;226m"
    state_colour = "\033[92m" if state.lower() == "up" else "\033[91m"
    if mode_raw.lower() == "managed":
        mode_colour = "\033[92m"
    elif mode_raw.lower() == "monitor":
        mode_colour = "\033[91m"
    elif mode_raw.lower() == "ap":
        mode_colour = "\033[93m"
    else:
        mode_colour = "\033[0m"

    print(f"[ Interface       ] {interface_colour}{interface}\033[0m")
    print(f"[ Interface State ] {state_colour}{state}\033[0m")
    print(f"[ Interface Mode  ] {mode_colour}{mode}\033[0m")
    print()

import time

def print_service_status():
    """Display Access Point status with time-based expiry, NAT state, and BSSID."""
    ap_file = "/tmp/wapt_ap_active"
    ap_raw = "Stopped"

    # Expiry threshold in seconds (15 minutes)
    expiry_seconds = 900  # 15 minutes

    if os.path.exists(ap_file):
        try:
            with open(ap_file, "r") as f:
                content = f.read().strip()
                parts = content.split("|")

                if len(parts) >= 3:
                    ssid = parts[0]
                    timestamp = int(parts[1])
                    nat_flag = parts[2]
                    bssid = parts[3] if len(parts) > 3 else "default"

                    age = time.time() - timestamp

                    if age <= expiry_seconds:
                        nat_status = "NAT" if nat_flag == "nat" else "No NAT"
                        bssid_display = f", BSSID {bssid}" if bssid != "default" else ""
                        ap_raw = f"Running ({ssid}, {nat_status}{bssid_display})"
        except Exception:
            pass  # If error ap_raw = "Stopped"

    ap_colour = "\033[92m" if ap_raw.startswith("Stopped") else "\033[93m"
    print(f"[ Access Point ] {ap_colour}{ap_raw}\033[0m")
    print()

def print_subtitle():
    print_header()
    print()
    print_divider()

    print_interface_status()
    print_service_status()
    print_divider()

def show_menu():
    """Display main menu."""
    clear_screen()
    
    # Generate ASCII banner
    ascii_banner = pyfiglet.figlet_format("WAPT", font="ansi_shadow")
    print("\033[93m" + ascii_banner + "\033[0m")
    print_header()
    print()
    print_divider()

    # Display interface status
    print_interface_status()

    # Display service status
    print_service_status()

    # Generate menu
    print_divider()
    print_header("Standalone Tools")
    print("  [1] Access Points")
    print()
    print_header("Utilities")
    print("  [2] Service Control")
    print("  [3] Help | About")

    print("\n  [0] Exit")

def run_bash_script(script_name, pause=True, capture=True, title=None, args=None, clear=True):
    """
    Executes a Bash script located under /src/bash.
    
    Args:
        script_name (str): Script name without extension (no .sh)
        args (list): List of arguments to pass to the script
        ...
    """
    if clear:
        clear_screen()

    if title:
        print_header(title)
        print()

    # Script full path
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bash", f"{script_name}.sh")
    )

    if not os.path.exists(script_path):
        print(f"[!] Script not found: {script_name}.sh")
        return

    cmd = ["bash", script_path]
    if args:
        cmd.extend(args)

    try:
        if capture:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout.strip())
        else:
            subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"[!] Script failed: {script_name}.sh")
        if e.stderr:
            print(e.stderr.strip())

    if pause:
        input("\n[Press Enter to return to menu]")

def prompt_nat():
    """Prompt user to enable NAT."""
    response = input("\n  [+] Enable NAT forwarding for this profile? [y/N]: ").strip().lower()
    return ["nat"] if response == "y" else []

import re

def generate_bssid(profile_number: int) -> str:
    """Generate a locally administered MAC address with profile-specific last octet."""
    # First byte 0x02 = locally administered
    base = [0x02, 0x00, 0x00, 0x00, 0x00, profile_number]
    return ":".join(f"{octet:02X}" for octet in base)

def ap_profiles():
    """Access Points submenu."""

    def ap_open(args):
        run_bash_script("start-ap", args=["ap_open"] + args, capture=False, pause=True, title="Open Access Point")

    def ap_wpa2(args):
        run_bash_script("start-ap", args=["ap_wpa2"] + args, capture=False, pause=True, title="WPA2 Access Point")

    def ap_hidden(args):
        run_bash_script("start-ap", args=["ap_wpa2-hidden"] + args, capture=False, pause=True, title="Hidden SSID Access Point")

    def ap_spoofed(args):
        run_bash_script("start-ap", args=["ap_spoofed"] + args, capture=False, pause=True, title="Spoofed SSID Access Point")

    def ap_misconfig(args):
        run_bash_script("start-ap", args=["ap_misconfig"] + args, capture=False, pause=True, title="Misconfigured Access Point")

    def ap_wpa3(args):
        run_bash_script("start-ap", args=["ap_wpa3"] + args, capture=False, pause=True, title="WPA3 Access Point")

    def stop_ap():
        run_bash_script("stop-ap", pause=True, capture=False, title="Stop Access Point")

    actions = {
        "1": ap_open,
        "2": ap_wpa2,
        "3": ap_hidden,
        "4": ap_spoofed,
        "5": ap_misconfig,
        "6": ap_wpa3,
        "S": stop_ap
    }

    while True:
        clear_screen()

        print_subtitle()

        print_header("Standalone Access Point Profiles")
        print()

        print("  [1] Launch OPN Access Point (Unencrypted)")
        print("  [2] Launch WPA2 Personal Personal Access Point (WPA2-PSK)")
        print("  [3] Launch Hidden SSID Access Point (WPA2-PSK)")
        print("  [4] Launch Spoofed SSID Access Point (OPN)")
        print("  [5] Launch Misconfigured Access Point (WPA1-TKIP)")
        print("  [6] Launch WPA3 Access Point (WPA3-SAE)")

        print("\n  [S] Stop Access Point")

        print("\n  [0] Return to Main Menu")

        choice = input("\n  [+] Select an option: ").strip().upper()

        if choice == "0":
            break

        if choice in actions:
            if choice in {"1", "2", "3", "4", "5", "6"}:
                if os.path.exists("/tmp/wapt_ap_active"):
                    print("\n\033[91m  [!] An access point is already running.\033[0m")
                    input("\n[Press Enter to return to menu]")
                    continue  # Return to submenu without prompting for NAT

                # NAT prompt
                nat_args = prompt_nat()

                # BSSID prompt
                use_bssid = input("  [+] Use a custom (locally administered) BSSID? [y/N]: ").strip().lower()
                if use_bssid == "y":
                    profile_map = {
                        "1": 1,
                        "2": 2,
                        "3": 3,
                        "4": 4,
                        "5": 5,
                        "6": 6
                    }
                    profile_number = profile_map.get(choice, 0)
                    generated_bssid = generate_bssid(profile_number)
                    print(f"  [✓] Using generated BSSID: {generated_bssid}")
                    os.environ["BSSID"] = generated_bssid
                else:
                    os.environ.pop("BSSID", None)

                actions[choice](nat_args)  # Call AP launcher with args

            else:
                clear_screen()
                actions[choice]()  # Stop AP or other non-arg actions
        else:
            pause_on_invalid()

def service_control():
    """Service Control submenu."""

    def interface_state():
        """Interface State submenu."""

        def set_interface_down():
            run_bash_script("set-interface-down", pause=False, capture=False, title="Change Interface State")

        def set_interface_up():
            run_bash_script("set-interface-up", pause=False, capture=False, title="Change Interface State")

        actions = {
            "1": set_interface_down,
            "2": set_interface_up
        }

        while True:
            clear_screen()

            print_subtitle()

            print_header("Change Interface State")
            print()
                    
            print("  [1] Set current interface DOWN")
            print("  [2] Bring current interface UP")

            print("\n  [0] Return to Service Control Menu")

            choice = input("\n  [+] Select an option: ")

            if choice == "0":
                break

            action = actions.get(choice)
            if action:
                clear_screen()
                action()
            else:
                pause_on_invalid()

    def interface_mode():
        """Interface mode submenu."""

        def switch_to_managed():
            run_bash_script("set-mode-managed", pause=False, capture=False, title="Change Interface Mode")

        def switch_to_monitor():
            run_bash_script("set-mode-monitor", pause=False, capture=False, title="Change Interface Mode")

        actions = {
            "1": switch_to_managed,
            "2": switch_to_monitor
        }

        while True:
            clear_screen()

            print_subtitle()

            print_header("Change Interface Mode")
            print()

            print("  [1] Switch to Managed mode")
            print("  [2] Switch to Monitor mode")

            print("\n  [0] Return to Service Control Menu")

            choice = input("\n  [+] Select an option: ")

            if choice == "0":
                break

            action = actions.get(choice)
            if action:
                clear_screen()
                action()
            else:
                pause_on_invalid()

    def interface_reset():
        """Reset interface submenu."""

        def perform_soft_reset():
            run_bash_script("reset-interface-soft", pause=False, capture=False, title="Reset Interface (Soft)")

        def perform_hard_reset():
            run_bash_script("reset-interface-hard", pause=False, capture=False, title="Reset Interface (Hard)")

        actions = {
            "1": perform_soft_reset,
            "2": perform_hard_reset
        }

        while True:
            clear_screen()

            print_subtitle()

            print_header("Reset Interface")
            print()

            print("  [1] Perform Soft Reset (Interface Down/Up)")
            print("  [2] Perform Hard Reset (Interface Unload/Reload)")

            print("\n  [0] Return to Service Control Menu")

            choice = input("\n  [+] Select an option: ")

            if choice == "0":
                break

            action = actions.get(choice)
            if action:
                clear_screen()
                action()
            else:
                pause_on_invalid()

    actions = {
        "1": interface_state,
        "2": interface_mode,
        "3": interface_reset
    }

    while True:
        clear_screen()

        print_subtitle()

        print_header("Service Control")
        print()

        print("  [1] Change Interface State")
        print("  [2] Change Interface Mode")
        print("  [3] Reset Interface")

        print("\n  [0] Return to Main Menu")

        choice = input("\n  [+] Select an option: ")

        if choice == "0":
            break

        action = actions.get(choice)
        if action:
            clear_screen()
            action()
        else:
            pause_on_invalid()

def help_about():
    """Help | About submenu."""

    clear_screen()

    print_subtitle()

    print_header("Help | About")

    print("\nThis tool provides a simple CLI interface to control")
    print("a wireless access point using preconfigured Bash scripts.")

    print("\nAuthor: Paul Smurthwaite")
    print("Module: TM470-25B")

    input("\n[Press Enter to return to menu]")

def main():
    """User input handler."""

    while True:
        show_menu()
        choice = input("\n  [+] Select an option: ")
        
        if choice == "1":
            ap_profiles()
        elif choice == "2":
            service_control()
        elif choice == "3":
            help_about()
        elif choice == "0":
            if os.path.exists("/tmp/wapt_ap_active"):
                print("\n[!] An access point is still running. Shutting it down...")
                run_bash_script("stop-ap", pause=False, capture=False, clear=False)

            print("\nExiting to shell.")
            break

        else:
            pause_on_invalid()

if __name__ == "__main__":
    main()
