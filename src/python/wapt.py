#!/usr/bin/env python3
"""wapt.py

Main entry point for the Wireless Access Point Toolkit (WAPT) menu interface.

This script provides a simple, operator-friendly CLI for accessing key toolkit functions such as scanning, capturing, and detection.  It is designed to offer a clear and low-complexity user experience, suitable for field use in SME environments.

The menu system acts as the central launcher for Bash and Python-based components of the toolkit, with screen clearing and section redrawing used to improve usability without introducing graphical complexity.

Author:      Paul Smurthwaite
Date:        2025-05-16
Module:      TM470-25B
"""

import os
import pyfiglet
import re
import subprocess
import sys
import time
import datetime
from pathlib import Path

LOG_FILE = "logs/wapt_session.log"
AP_ACTIVE_FILE = "/tmp/ap_active"

# Define version and date at the top for easy update
APP_VERSION = "v1.2"
APP_DATE = "2025-05-17"

# ─── UI Helpers ───
# Theme Config
COLOURS_DARK = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "header": "\033[93m",  # yellow
    "info":   "\033[96m",  # cyan
    "success":"\033[92m",  # green
    "warning":"\033[91m",  # red
    "neutral":"\033[90m"   # grey
}

COLOURS_LIGHT = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "header": "\033[94m",  # blue
    "info":   "\033[36m",  # teal
    "success":"\033[32m",  # dark green
    "warning":"\033[31m",  # red/maroon
    "neutral":"\033[30m"   # black/grey
}

COLOURS_HIGH_CONTRAST = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "header": "\033[97m",  # Bright white
    "info":   "\033[96m",  # Cyan
    "success":"\033[92m",  # Bright green
    "warning":"\033[91m",  # Bright red
    "neutral":"\033[97m"   # Bright white again
}

COLOURS_MONOCHROME = {
    "reset":  "",
    "bold":   "",
    "header": "",
    "info":   "",
    "success":"",
    "warning":"",
    "neutral":""
}

THEME_MODE = "dark"
if "--light" in sys.argv:
    THEME_MODE = "light"
elif "--high-contrast" in sys.argv:
    THEME_MODE = "high-contrast"
elif "--monochrome" in sys.argv:
    THEME_MODE = "monochrome"

if THEME_MODE == "dark":
    COLOURS = COLOURS_DARK
elif THEME_MODE == "light":
    COLOURS = COLOURS_LIGHT
elif THEME_MODE == "high-contrast":
    COLOURS = COLOURS_HIGH_CONTRAST
elif THEME_MODE == "monochrome":
    COLOURS = COLOURS_MONOCHROME
else:
    COLOURS = COLOURS_DARK  # Fallback default

# UI Colour
def colour(text, style):
    """
    Apply ANSI colour styling to text based on the current theme.

    Args:
        text (str): The text to style.
        style (str): The style key (e.g., 'header', 'info', 'success').

    Returns:
        str: The styled text with ANSI codes.
    """
    return f"{COLOURS.get(style, '')}{text}{COLOURS['reset']}"

# UI Banner
def ui_banner():
    """
    Display the ASCII art banner for the application using the current theme's header colour.
    """
    # Use pyfiglet to generate the banner dynamically
    ascii_banner = pyfiglet.figlet_format("WAPT", font="ansi_shadow")
    print(colour(ascii_banner, "header"))

# UI Header
def ui_header(title="Wireless Access Point Toolkit"):
    """
    Display a section header. If the main title, includes version and date.

    Args:
        title (str): The header text to display. Defaults to the main app title.
    """
    if title == "Wireless Access Point Toolkit":
        styled = f"{COLOURS['bold']}{COLOURS['header']}[ {title} {APP_VERSION} – {APP_DATE} ]{COLOURS['reset']}"
    else:
        styled = f"{COLOURS['bold']}{COLOURS['header']}[ {title} ]{COLOURS['reset']}"
    print(styled)

# UI Divider
def ui_divider():
    """
    Print a horizontal divider line in the UI using the neutral colour.
    """
    print(colour("-----------------------------------", "neutral"))
    print()

# UI Subtitle
def ui_subtitle():
    """
    Display a subtitle block: divider, interface status, service status, divider.
    """
    ui_divider()
    print_interface_status()
    print_service_status()
    ui_divider()

# UI Standard Header
def ui_standard_header(menu_title=None):
    """
    Render the standard UI header block: banner, main title, subtitle, and optional menu title.

    Args:
        menu_title (str, optional): If provided, displays this as a section header after the main title.
    """
    ui_banner()       # ASCII banner
    ui_header()       # Toolkit title
    print()
    ui_subtitle()     # Divider + interface + service info

    if menu_title:
        ui_header(menu_title)  # Current menu title
        print()

# UI Clear Screen
def ui_clear_screen():
    """
    Clear the terminal screen using the appropriate command for the OS.
    """
    os.system("cls" if os.name == "nt" else "clear")

# UI Invalid Option
def ui_pause_on_invalid():
    """
    Display an invalid input warning and pause for user acknowledgment.
    """
    print(colour("\n[!] Invalid option. Please try again.", "warning"))
    input("[Press Enter to continue]")

# ─── Display Interface ───
# 
def print_interface_status():
    """
    Print the current wireless interface, its state, and mode, with colour coding.
    """
    interface, state_raw, mode_raw = get_interface_details()

    state = state_raw.title()
    mode = "AP" if mode_raw.lower() == "ap" else mode_raw.title()

    # Determine colours
    interface_display = colour(interface, "info")
    state_display = colour(state, "success" if state.lower() == "up" else "warning")

    if mode_raw.lower() == "managed":
        mode_display = colour(mode, "success")
    elif mode_raw.lower() == "monitor":
        mode_display = colour(mode, "warning")
    elif mode_raw.lower() == "ap":
        mode_display = colour(mode, "warning")
    else:
        mode_display = colour(mode, "reset")

    # Output
    print(f"[ Interface       ] {interface_display}")
    print(f"[ Interface State ] {state_display}")
    print(f"[ Interface Mode  ] {mode_display}")
    print()

# ─── Display Service ───
# 
def print_service_status():
    """
    Display the current Access Point status, including expiry, NAT state, and BSSID.
    Reads from /tmp/ap_active and shows 'Running' or 'Stopped' with details.
    """
    ap_raw = "Stopped"

    # Expiry threshold
    expiry_seconds = 900

    if os.path.exists(AP_ACTIVE_FILE):
        try:
            with open(AP_ACTIVE_FILE, "r") as f:
                content = f.read().strip()
                parts = content.split("|")

                # Expecting at least 4 parts: timestamp|ssid|bssid|channel
                # A 5th part for NAT status is optional for backward compatibility.
                if len(parts) >= 4:
                    timestamp = int(parts[0])
                    ssid = parts[1] or "N/A"
                    bssid = parts[2] or "N/A"
                    channel = parts[3] or "N/A"
                    nat_status = parts[4] if len(parts) >= 5 else None

                    age = time.time() - timestamp

                    if age <= expiry_seconds:
                        start_time = time.strftime("%H:%M:%S", time.localtime(timestamp))
                        if nat_status:
                            ap_raw = f"Running ({start_time}, {ssid}, CH {channel}, {nat_status}, BSSID {bssid})"
                        else:
                            ap_raw = f"Running ({start_time}, {ssid}, CH {channel}, BSSID {bssid})"
        except Exception as e:
            log_event(f"ERROR: Could not read AP status file {AP_ACTIVE_FILE}: {e}")

    style = "success" if ap_raw == "Stopped" else "warning"
    print(f"[ Access Point ] {colour(ap_raw, style)}")
    print()

# ─── Interface Helpers ───
#
def get_interface_details():
    """
    Get the current wireless interface details by running a helper bash script.

    Returns:
        tuple: (interface, state, mode) as strings.
    """
    # Base directory for bash scripts
    base_path = Path(__file__).parent.parent / "bash"
    script_path = (base_path / "services" / "interface-ctl.sh").resolve()

    # Security check: ensure the script is within the bash directory and exists
    if not script_path.is_file() or base_path not in script_path.parents:
        return ("[!] Not found", "[!] Not found", "[!] Not found")

    try:
        # Use string representation of the Path object for the command
        result = subprocess.run(["bash", str(script_path), "status"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        interface = lines[0].split(":")[1].strip().upper() if len(lines) > 0 else "?"
        state     = lines[1].split(":")[1].strip().upper() if len(lines) > 1 else "?"
        mode      = lines[2].split(":")[1].strip().upper() if len(lines) > 2 else "?"
        return (interface, state, mode)
    except subprocess.CalledProcessError:
        return ("[!] Script error", "[!] Script error", "[!] Script error")

def get_current_interface():
    """
    Get the current wireless interface name.

    Returns:
        str: The interface name.
    """
    return get_interface_details()[0]

def get_interface_state():
    """
    Get the current wireless interface state.

    Returns:
        str: The interface state.
    """
    return f"State:     {get_interface_details()[1]}"

def get_interface_mode():
    """
    Get the current wireless interface mode.

    Returns:
        str: The interface mode.
    """
    return f"Mode:      {get_interface_details()[2]}"

# ─── Theme Management ───
def set_theme(mode):
    """
    Set the global theme mode and update the COLOURS dictionary.

    Args:
        mode (str): The theme mode to set ('dark', 'light', 'high-contrast', 'monochrome').
    """
    global THEME_MODE, COLOURS
    THEME_MODE = mode
    if mode == "dark":
        COLOURS = COLOURS_DARK
    elif mode == "light":
        COLOURS = COLOURS_LIGHT
    elif mode == "high-contrast":
        COLOURS = COLOURS_HIGH_CONTRAST
    elif mode == "monochrome":
        COLOURS = COLOURS_MONOCHROME
    else:
        COLOURS = COLOURS_DARK

# Initialize theme from CLI args (moved from top-level)
if __name__ == "__main__":
    # Initialize theme based on command-line arguments
    if "--light" in sys.argv:
        set_theme("light")
    elif "--high-contrast" in sys.argv:
        set_theme("high-contrast")
    elif "--monochrome" in sys.argv:
        set_theme("monochrome")
    else:
        set_theme("dark")

# ─── Display Main Menu ───
# 
def show_menu():
    """
    Display the main menu, including current theme, and handle no user input.
    """
    ui_clear_screen()
    
    # Header block
    ui_standard_header("Main Menu")

    # Menu block
    ui_header("Utilities")
    print("[1] Access Points")
    print()
    ui_header("Services")
    print("[2] Service Control")
    print()
    # Show current theme in the menu
    theme_label = THEME_MODE.replace("-", " ").title()
    print(f"[3] Change Theme [{theme_label}]")
    print("[4] Help | About")

    # Exit option
    print("\n[0] Exit")

# ─── Bash Script Handler ───
#
def run_bash_script(script_name, pause=True, capture=True, args=None, clear=True, title=None):
    """
    Executes a Bash script located under /src/bash. Handles errors and logs events.

    Args:
        script_name (str): Script name without extension (no .sh).
        pause (bool): If True, pauses after execution.
        capture (bool): If True, captures and prints script output.
        args (list, optional): Arguments to pass to the script.
        clear (bool): If True, clears the screen before running.
        title (str, optional): Title to display before running.

    Returns:
        None

    Side Effects:
        Prints output to terminal. Logs errors to session log.
    """
    if clear:
        ui_clear_screen()

    if title:
        ui_header(title)
        print()

    # Base directory for bash scripts
    base_path = Path(__file__).parent.parent / "bash"

    # Resolve the script path safely
    script_path = (base_path / f"{script_name}.sh").resolve()

    # Security check: ensure the script is within the bash directory and exists
    if not script_path.is_file() or base_path not in script_path.parents:
        error_msg = f"Script not found or invalid path: {script_name}.sh"
        print(colour(f"[x] {error_msg}", "warning"))
        log_event(f"ERROR: {error_msg}")
        return

    # Use string representation of the Path object for the command
    cmd = ["bash", str(script_path)]
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
        failed_command = " ".join(e.cmd)
        error_msg = f"Script failed: {script_name}.sh"
        log_msg = f"ERROR: {error_msg} | Command: '{failed_command}' | Stderr: {e.stderr.strip() if e.stderr else 'N/A'}"
        print(colour(f"[x] {error_msg}", "warning"))
        if e.stderr:
            print(e.stderr.strip())
        log_event(log_msg)
    except Exception as e:
        error_msg = f"[x] Unexpected error running script: {script_name}.sh"
        print(colour(error_msg, "warning"))
        print(e)
        log_event(f"UNEXPECTED ERROR: {error_msg} | {str(e)}")

    if pause:
        input("\n[Press Enter to return to menu]")

def prompt_nat():
    """
    Prompt the user to enable NAT forwarding for the selected AP profile.

    Returns:
        list: ["nat"] if enabled, otherwise an empty list.
    """
    response = input(f"[{colour('?', 'header')}] Enable NAT forwarding for this profile? [Y/n]: ").strip().lower()
    return ["nat"] if response != "n" else []

def generate_bssid(profile_number: int) -> str:
    """
    Generate a locally administered MAC address with a profile-specific last octet.

    Args:
        profile_number (int): The AP profile number to encode in the MAC address.

    Returns:
        str: The generated MAC address as a string.
    """
    # First byte 0x02 = locally administered
    base = [0x02, 0x00, 0x00, 0x00, 0x00, profile_number]
    return ":".join(f"{octet:02X}" for octet in base)

def log_event(message):
    """
    Append a timestamped event to the session log file. Ensures the logs directory exists.
    Logs file write errors to stderr.

    Args:
        message (str): The event message to log.
    """
    # Ensure logs directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} | {message}\n")
    except Exception as e:
        print(colour("[x] Failed to write to log file.", "warning"))
        print(e)

AP_PROFILES = [
    {"id": "T001", "desc": "Open", "config": "ap_t001", "pause": True},
    {"id": "T003", "desc": "Open", "config": "ap_t003_1", "pause": True},
    {"id": "T003", "desc": "WPA2", "config": "ap_t003_2", "pause": True},
    {"id": "T003", "desc": "WPA2 Hidden SSID", "config": "ap_t003_3", "pause": True},
    {"id": "T003", "desc": "Misconfigured", "config": "ap_t003_4", "pause": True},
    {"id": "T004", "desc": "WPA2", "config": "ap_t004", "pause": True},
    {"id": "T005", "desc": "WPA2", "config": "ap_t005", "pause": True},
    {"id": "T006", "desc": "Misconfigured", "config": "ap_t006", "pause": True},
    {"id": "T007", "desc": "WPA2", "config": "ap_t007", "pause": True},
    {"id": "T009", "desc": "WPA2", "config": "ap_t009", "pause": True},
    {"id": "T014", "desc": "Open", "config": "ap_t014", "pause": True},
    {"id": "T015", "desc": "Open", "config": "ap_t015", "pause": True},
    {"id": "T016", "desc": "Open", "config": "ap_t016", "pause": True},
]

def ap_profiles():
    """
    Display the Access Points submenu, allowing the user to launch or stop AP profiles.
    Handles user input and logs AP launches.
    """
    def stop_ap():
        log_event("Action: Stop Access Point")
        run_bash_script("utilities/stop-ap", pause=True, capture=False, clear=True, title="Stop Access Point")

    while True:
        ui_clear_screen()

        # Header block
        ui_standard_header("Standalone Access Point Profiles")

        # Menu block - generated from AP_PROFILES
        for i, profile in enumerate(AP_PROFILES, 1):
            print(f"[{i}] Launch {profile['id']}: {profile['desc']}")

        print("\n[S] Stop Access Point")
        print("\n[0] Return to Main Menu")

        # Input
        choice = input(f"\n[{colour('?', 'header')}] Select an option: ").strip().upper()

        if choice == "0": break
        if choice == "S":
            stop_ap()
            continue

        try:
            profile_index = int(choice) - 1
            if not 0 <= profile_index < len(AP_PROFILES):
                raise ValueError
        except ValueError:
            ui_pause_on_invalid()
            continue

        if os.path.exists(AP_ACTIVE_FILE):
            print(colour("\n[!] An access point is already running.", "warning"))
            input("\n[Press Enter to return to menu]")
            continue

        # Get selected profile
        profile = AP_PROFILES[profile_index]
        title = f"{profile['id']}: {profile['desc']}"

        # Get launch arguments, starting with the profile config name
        args = [profile["config"]]
        # Prompt for NAT and add 'nat' to args if user agrees
        args.extend(prompt_nat())

        # Prompt for custom BSSID
        os.environ.pop("BSSID", None)
        bssid_choice = input(f"[{colour('?', 'header')}] Use a custom BSSID for this profile? [y/N]: ").strip().lower()
        if bssid_choice == 'y':
            bssid = generate_bssid(profile_index + 1)
            os.environ["BSSID"] = bssid
            log_event(f"Set custom BSSID: {bssid}")

        log_event(f"Launched AP profile: {title} with args {args}")

        # Launch the AP script
        run_bash_script(
            "utilities/start-ap",
            args=args,
            capture=False,
            pause=profile["pause"],
            clear=True, # Clear screen after prompts for cleaner script output
            title=title
        )

def service_control():
    """
    Display the Service Control menu, providing access to interface and service management.
    Handles user input and calls relevant submenus.
    """

    def show_dhcp_leases():
        # Corrected to call the right script and to clear the screen.
        run_bash_script("services/show-ap-dhcp", pause=True, capture=True, clear=True, title="DHCP Lease Table")

    def show_connected_stations():
        # Corrected to clear the screen.
        run_bash_script("services/show-ap-stations", pause=True, capture=True, clear=True, title="Connected Stations")

    def show_session_log():
        """Displays the content of the session log file."""
        ui_header("Session Log")
        print()
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r") as f:
                    log_content = f.read().strip()
                    if log_content:
                        print(log_content)
                    else:
                        print(colour("[i] Session log is empty.", "info"))
            except Exception as e:
                print(colour(f"[x] Error reading log file: {e}", "warning"))
        else:
            print(colour("[!] Session log file not found.", "warning"))
        input("\n[Press Enter to return to menu]")

    def archive_session_log():
        """Archives the current session log by renaming it with a timestamp."""
        ui_header("Archive Session Log")
        print()
        if not os.path.exists(LOG_FILE):
            print(colour("[!] No session log found to archive.", "warning"))
        else:
            try:
                # Construct the new filename
                log_path = Path(LOG_FILE)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                archive_filename = f"wapt_session_{timestamp}.log"
                archive_path = log_path.with_name(archive_filename)

                # Rename the file
                log_path.rename(archive_path)

                # Log the event to the *new* log file that will be created
                log_event(f"Previous log archived to {archive_filename}")
                print(colour("[+] Session log successfully archived to:", "success"))
                print(f"  {archive_path}")

            except OSError as e:
                error_msg = f"Failed to archive log file: {e}"
                print(colour(f"[x] {error_msg}", "warning"))
                log_event(f"ERROR: {error_msg}")

        input("\n[Press Enter to return to menu]")

    def interface_state():
        """
        Interface State submenu.
        """

        while True:
            ui_clear_screen()

            # Header block
            ui_standard_header("Set Interface State")

            # Menu block                    
            print("[1] Set interface state DOWN")
            print("[2] Set interface state UP")
            print("\n[0] Return to Service Control Menu")

            # Input
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

            if choice == "1":
                log_event("Interface State: Action 'Set Down'")
                print()
                run_bash_script("services/interface-ctl", args=["down"], pause=True, capture=False, clear=False, title="Change Interface State")
            elif choice == "2":
                log_event("Interface State: Action 'Set Up'")
                print()
                run_bash_script("services/interface-ctl", args=["up"], pause=True, capture=False, clear=False, title="Change Interface State")
            elif choice == "0":
                break
            else:
                ui_pause_on_invalid()

    def interface_mode():
        """
        Interface mode submenu.
        """

        while True:
            ui_clear_screen()

            # Header block
            ui_standard_header("Set Interface Mode")
            
            # Menu block
            print("[1] Set interface mode MANAGED")
            print("[2] Set interface mode MONITOR")
            print("\n[0] Return to Service Control Menu")

            # Input
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

            if choice == "1":
                log_event("Interface Mode: Action 'Set to Managed'")
                print()
                run_bash_script("services/interface-ctl", args=["mode", "managed"], pause=False, capture=False, clear=False, title="Change Interface Mode")
            elif choice == "2":
                log_event("Interface Mode: Action 'Set to Monitor'")
                print()
                run_bash_script("services/interface-ctl", args=["mode", "monitor"], pause=False, capture=False, clear=False, title="Change Interface Mode")
            elif choice == "0":
                break
            else:
                ui_pause_on_invalid()

    def interface_reset():
        """
        Reset interface submenu.
        """

        while True:
            ui_clear_screen()

            # Header block
            ui_standard_header("Reset Interface")
            
            # Menu block
            print("[1] Interface soft reset (Down/Up)")
            print("[2] Interface hard reset (Unload/Reload)")
            print("\n[0] Return to Service Control Menu")

            # Input
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

            if choice == "1":
                log_event("Reset Interface: Action 'Soft Reset'")
                print()
                run_bash_script("services/interface-ctl", args=["reset", "soft"], pause=False, capture=False, clear=False, title="Reset Interface (Soft)")
            elif choice == "2":
                log_event("Reset Interface: Action 'Hard Reset'")
                print()
                run_bash_script("services/interface-ctl", args=["reset", "hard"], pause=False, capture=False, clear=False, title="Reset Interface (Hard)")
            elif choice == "0":
                break
            else:
                ui_pause_on_invalid()

    while True:
        ui_clear_screen()

        # Header block
        ui_standard_header("Service Control")

        # Menu block
        print("[1] Interface State")
        print("[2] Interface Mode")
        print("[3] Reset Interface")
        print("[4] Show DHCP Leases")
        print("[5] Show Connected Stations")
        print("[6] Show Session Log")
        print("[7] Archive Session Log")
        print("\n[0] Return to Main Menu")

        # Input
        choice = input(f"\n[{colour('?', 'header')}] Select an option: ")

        if choice == "1":
            log_event("Service Control: Selected 'Interface State'")
            ui_clear_screen()
            interface_state()
        elif choice == "2":
            log_event("Service Control: Selected 'Interface Mode'")
            ui_clear_screen()
            interface_mode()
        elif choice == "3":
            log_event("Service Control: Selected 'Reset Interface'")
            ui_clear_screen()
            interface_reset()
        elif choice == "4":
            log_event("Service Control: Selected 'Show DHCP Leases'")
            show_dhcp_leases()
        elif choice == "5":
            log_event("Service Control: Selected 'Show Connected Stations'")
            show_connected_stations()
        elif choice == "6":
            log_event("Service Control: Selected 'Show Session Log'")
            show_session_log()
        elif choice == "7":
            log_event("Service Control: Selected 'Archive Session Log'")
            ui_clear_screen()
            archive_session_log()
        elif choice == "0":
            break
        else:
            ui_pause_on_invalid()

def help_about():
    """
    Display the Help | About submenu, including inclusivity features and project info.
    """
    ui_clear_screen()
    # Header block
    ui_standard_header("Help | About")
    print(colour("Inclusivity & Accessibility Features:", "header"))
    print("  • Multiple colour themes: Dark, Light, High Contrast, Monochrome")
    print("  • High-contrast and monochrome modes for low vision and colourblind users")
    print("  • Fully keyboard-navigable menu system")
    print("  • Clear, consistent prompts and colour cues throughout the UI")
    print("  • Accessible to users with limited command-line experience")
    print()
    print("This tool provides a command-line interface for managing")
    print("wireless access point profiles in a structured testbed environment.")
    print()
    print("Functions include:")
    print("  • Launching access points with varied encryption and visibility modes")
    print("  • Applying optional NAT and custom BSSID configurations")
    print("  • Stopping services and restoring network state")
    print("  • Monitoring interface and AP status via the Service Status panel")
    print()
    print("All operations are driven by modular Bash scripts, coordinated")
    print("through a unified Python menu for SME-friendly field usage.")
    print()
    print(f"Author : Paul Smurthwaite")
    print(f"Module : TM470-25B")
    print(f"Version: {APP_VERSION}")
    print(f"Date   : {APP_DATE}")
    # Input
    input("\n[Press Enter to return to menu]")

def theme_menu():
    """
    Display the theme selection submenu, allowing the user to change the colour theme.
    Handles user input and logs theme changes.
    """
    while True:
        ui_clear_screen()
        ui_standard_header("Change Theme")
        print("Select a theme:\n")
        print("[1] Dark (default)")
        print("[2] Light")
        print("[3] High Contrast")
        print("[4] Monochrome")
        print("\n[0] Return to Main Menu")
        choice = input(f"\n[{colour('?', 'header')}] Select a theme: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            set_theme("dark")
            log_event("Theme changed to 'Dark'")
            print(colour("\n[+] Theme changed to Dark.", "success"))
            input("[Press Enter to continue]")
            break
        elif choice == "2":
            set_theme("light")
            log_event("Theme changed to 'Light'")
            print(colour("\n[+] Theme changed to Light.", "success"))
            input("[Press Enter to continue]")
            break
        elif choice == "3":
            set_theme("high-contrast")
            log_event("Theme changed to 'High Contrast'")
            print(colour("\n[+] Theme changed to High Contrast.", "success"))
            input("[Press Enter to continue]")
            break
        elif choice == "4":
            set_theme("monochrome")
            log_event("Theme changed to 'Monochrome'")
            print(colour("\n[+] Theme changed to Monochrome.", "success"))
            input("[Press Enter to continue]")
            break
        else:
            log_event(f"Theme menu: Invalid option '{choice}'")
            ui_pause_on_invalid()

def check_dependencies():
    """
    Checks for required system dependencies by running a helper script.
    Exits gracefully if any dependency is missing.
    """
    ui_clear_screen()
    print(colour("Checking system dependencies...", "info"))

    # envsubst (from gettext) is critical for config templating
    dependencies = ["hostapd", "dnsmasq", "iptables", "envsubst"]
    base_path = Path(__file__).parent.parent / "bash"
    script_path = (base_path / "utilities" / "check-deps.sh").resolve()

    if not script_path.is_file():
        print(colour("\n[x] Dependency checker script not found. Cannot continue.", "warning"))
        sys.exit(1)

    try:
        cmd = ["bash", str(script_path)] + dependencies
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(colour("[+] All dependencies are met.", "success"))
        time.sleep(1)
    except subprocess.CalledProcessError as e:
        print(colour("\n[!] Dependency check failed. The following packages are required:", "warning"))
        print(e.stderr.strip())
        print(colour("\nPlease install the missing packages and try again.", "warning"))
        sys.exit(1)
    except Exception as e:
        print(colour(f"\n[x] An unexpected error occurred during dependency check: {e}", "warning"))
        sys.exit(1)

def cleanup_temp_files():
    """
    Remove all temporary files created by the toolkit to ensure a clean state.
    """
    print(colour("\n[~] Cleaning up temporary files...", "neutral"))
    log_event("Action: Cleaning up temporary files")

    temp_files = [
        AP_ACTIVE_FILE,
        "/tmp/wapt_http_server.pid",
        "/tmp/hostapd.conf"
    ]

    for f_path in temp_files:
        try:
            if os.path.exists(f_path):
                os.remove(f_path)
                log_event(f"Removed temp file: {f_path}")
        except OSError as e:
            log_event(f"ERROR: Failed to remove temp file {f_path}: {e}")

def main():
    """
    Main user input handler and application loop. Handles menu navigation, logging, and error handling.
    """
    check_dependencies()
    log_event("Session started")
    try:
        while True:
            show_menu()
            choice = input(f"\n[{colour('?', 'header')}] Select an option: ").strip()
            if choice == "1":
                log_event("Main menu: Selected 'Access Points'")
                ap_profiles()
            elif choice == "2":
                log_event("Main menu: Selected 'Service Control'")
                service_control()
            elif choice == "3":
                log_event(f"Main menu: Selected 'Change Theme' (current: {THEME_MODE})")
                theme_menu()
            elif choice == "4":
                log_event("Main menu: Selected 'Help | About'")
                help_about()
            elif choice == "0":
                if os.path.exists(AP_ACTIVE_FILE):
                    print(colour("\n[!] Stopping running access point", "warning"))
                    run_bash_script("utilities/stop-ap", pause=False, capture=False, clear=False)
                cleanup_temp_files()
                print(colour("\n[+] Exiting to shell.", "warning"))
                log_event("Session ended")
                break
            else:
                log_event(f"Main menu: Invalid option '{choice}'")
                ui_pause_on_invalid()
    except KeyboardInterrupt:
        if os.path.exists(AP_ACTIVE_FILE):
            print(colour("\n[!] Stopping running access point due to user interrupt...", "warning"))
            run_bash_script("utilities/stop-ap", pause=False, capture=False, clear=False)
        cleanup_temp_files()
        print(colour("\n[!] Session interrupted by user.", "warning"))
        log_event("Session interrupted by user (KeyboardInterrupt)")
    except Exception as e:
        cleanup_temp_files()
        print(colour("[x] An unexpected error occurred. See log for details.", "warning"))
        log_event(f"UNEXPECTED ERROR: {str(e)}")

if __name__ == "__main__":
    main()
