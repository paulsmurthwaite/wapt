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
import subprocess

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

def print_service_status():
    """Display Access Point and Attack Tool status with colour formatting."""
    ap_file = "/tmp/watt_ap_active"
    atk_file = "/tmp/watt_attack_active"

    ap_raw = "Stopped"
    atk_raw = "Stopped"

    if os.path.exists(ap_file):
        with open(ap_file, "r") as f:
            ap_raw = f"Running ({f.read().strip()})"

    if os.path.exists(atk_file):
        with open(atk_file, "r") as f:
            atk_raw = f"Running ({f.read().strip()})"

    ap_colour = "\033[92m" if ap_raw.startswith("Stopped") else "\033[93m"
    atk_colour = "\033[92m" if atk_raw.startswith("Stopped") else "\033[91m"

    print(f"[ Access Point ] {ap_colour}{ap_raw}\033[0m")
    print(f"[ Attack Tool  ] {atk_colour}{atk_raw}\033[0m")
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
    print_header("Automated Testing")
    print("  [1] Threat Scenarios\n")

    print_header("Standalone Tools")
    print("  [2] Access Points")
    print("  [3] Attack Tools\n")

    print_header("Utilities")
    print("  [4] Service Control")
    print("  [5] Help | About")

    print("\n  [0] Exit")

def run_bash_script(script_name, pause=True, capture=True, title=None):
    """
    Executes a Bash script located under /src/bash.
    
    Args:
        script_name (str): Script name without extension.
        title (str): Optional header to display before execution
        pause (bool): Whether to wait for user input after execution.
    """
    clear_screen()

    if title:
        print_header(title)
        print()

    # Bash script path
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "bash", f"{script_name}.sh")
    )

    if not os.path.exists(script_path):
        print(f"[!] Script not found: {script_name}.sh")
        return
    
    try:
        if capture:
            result = subprocess.run(
                ["bash", script_path],
                check=True,
                capture_output=True,
                text=True
            )
        else:
            subprocess.run(["bash", script_path], check=True)
    
    except subprocess.CalledProcessError as e:
        print(f"[!] Script failed: {script_name}.sh")
        if e.stderr:
            print(e.stderr.strip())

    if pause:
        input("\n[Press Enter to return to menu]")

def threat_scenario():
    """Launch Threat Scenario submenu."""

    def threat_t001():
        run_bash_script("threat_t001", pause=True, title="T001 – Unencrypted Traffic Capture")

    def threat_t002():
        run_bash_script("threat_t002", pause=True, title="T002 – Probe Request Snooping")

    def threat_t004():
        run_bash_script("threat_t004", pause=True, title="T004 – Evil Twin Attack")

    def threat_t005():
        run_bash_script("threat_t005", pause=True, title="T005 – Open Rogue AP")

    def threat_t006():
        run_bash_script("threat_t006", pause=True, title="T006 – Misconfigured Access Point")

    def threat_t007():
        run_bash_script("threat_t007", pause=True, title="T007 – Deauthentication Flood")

    def threat_t009():
        run_bash_script("threat_t009", pause=True, title="T009 – Authentication Flood")

    def threat_t014():
        run_bash_script("threat_t014", pause=True, title="T014 – ARP Spoofing from Wireless Entry Point")

    def threat_t015():
        run_bash_script("threat_t015", pause=True, title="T015 – Malicious Hotspot Auto-Connect")

    def threat_t016():
        run_bash_script("threat_t016", pause=True, title="T016 – Directed Probe Response")

    actions = {
        "1":  threat_t001,
        "2":  threat_t002,
        "3":  threat_t004,
        "4":  threat_t005,
        "5":  threat_t006,
        "6":  threat_t007,
        "7":  threat_t009,
        "8":  threat_t014,
        "9":  threat_t015,
        "10": threat_t016
    }

    while True:
        clear_screen()

        print_subtitle()

        print_header("Threat Scenarios")
        print()

        print_header("Access Point Threats")
        print("  [1]  T001 – Unencrypted Traffic Capture")
        print("  [2]  T002 – Probe Request Snooping")
        print("  [3]  T004 – Evil Twin Attack")
        print("  [4]  T005 – Open Rogue AP")
        print("  [5]  T006 – Misconfigured Access Point")
        print()

        print_header("Client Exploits")
        print("  [6]  T007 – Deauthentication Flood")
        print("  [7]  T009 – Authentication Flood")
        print("  [8]  T014 – ARP Spoofing from Wireless Entry Point")
        print("  [9]  T015 – Malicious Hotspot Auto-Connect")
        print("  [10] T016 – Directed Probe Response")

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

def ap_profiles():
    """Access Points submenu."""

    def ap_open():
        run_bash_script("ap-open/start-ap", capture=False, pause=True, title="Open Access Point")

    def ap_wpa2():
        run_bash_script("ap-wpa2/start-ap", capture=False, pause=True, title="WPA2 Access Point")

    def ap_hidden():
        run_bash_script("ap-hiddenssid/start-ap", capture=False, pause=True, title="Hidden SSID Access Point")

    def ap_spoofed():
        run_bash_script("ap-spoofed/start-ap", capture=False, pause=True, title="Spoofed SSID Access Point")

    def ap_misconfig():
        run_bash_script("ap-misconfig/start-ap", capture=False, pause=True, title="Misconfigured Access Point")

    actions = {
        "1": ap_open,
        "2": ap_wpa2,
        "3": ap_hidden,
        "4": ap_spoofed,
        "5": ap_misconfig
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

def attack_tools():
    """Attack Tools submenu."""

    def run_deauth():
        run_bash_script("attack-deauth/attack.sh", pause=True, capture=False, title="T007 - Deauthentication Flood")

    def run_beacon():
        run_bash_script("attack-beacon/attack.sh", pause=True, capture=False, title="T008 - Beacon Flood")

    def run_auth():
        run_bash_script("attack-auth/attack.sh", pause=True, capture=False, title="T009 - Authentication Flood")

    def run_arp_spoof():
        run_bash_script("attack-arp/attack.sh", pause=True, capture=False, title="T014 - ARP Spoofing")

    def run_probe():
        run_bash_script("attack-probe/attack.sh", pause=True, capture=False, title="T016 - Directed Probe Response")

    actions = {
        "1": run_deauth,
        "2": run_beacon,
        "3": run_auth,
        "4": run_arp_spoof,
        "5": run_probe
    }

    while True:
        clear_screen()

        print_subtitle()

        print_header("Standalone Attack Tools")
        print()

        print("  [1] Launch Deauthentication Flood Attack (T007)")
        print("  [2] Launch Beacon Flood Attack (T008)")
        print("  [3] Launch Authentication Flood Attack (T009)")
        print("  [4] Launch ARP Spoofing Attack (T014)")
        print("  [5] Launch Directed Probe Response Attack (T016)")
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

def service_control():
    """Service Control submenu."""

    def stop_ap():
        run_bash_script("service/stop-ap", pause=True, capture=False, title="Stop Access Point")

    def stop_attacks():
        run_bash_script("service/stop-attacks", pause=True, capture=False, title="Stop All Attack Tools")

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
        "1": stop_ap,
        "2": stop_attacks,
        "3": interface_state,
        "4": interface_mode,
        "5": interface_reset
    }

    while True:
        clear_screen()

        print_subtitle()

        print_header("Service Control")
        print()

        print("  [1] Stop Access Point")
        print("  [2] Stop Attack Tools")
        print("  [3] Change Interface State")
        print("  [4] Change Interface Mode")
        print("  [5] Reset Interface")
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

def main():
    """User input handler."""

    while True:
        show_menu()
        choice = input("\n  [+] Select an option: ")
        
        if choice == "1":
            threat_scenario()
        elif choice == "2":
            ap_profiles()
        elif choice == "3":
            attack_tools()
        elif choice == "4":
            service_control()
        elif choice == "5":
            help_about()
        elif choice == "0":
            print("\nExiting to shell.")
            break
        else:
            pause_on_invalid()

if __name__ == "__main__":
    main()
