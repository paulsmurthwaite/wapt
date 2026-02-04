# Wireless Access Point Toolkit (WAPT)

## Overview
WAPT is a modular toolkit designed to launch simulated wireless access points. It supports security research by providing 13 scenario-aligned AP profiles (e.g., Evil Twin, Open Rogue) to generate traffic for the WSTT analysis engine.

## Engineering Philosophy
- **Modular Integration:** Built with a Bash/Python CLI integration to automate hostapd and dnsmasq configurations without operator input.
- **Accessibility Focus:** Includes high-contrast and monochrome modes, keyboard navigation, and consistent UI cues for diverse user needs.
- **Hardware Validation:** Optimised for Linux-compatible wireless adapters (Alfa AWUS036ACM) to ensure stable AP mode injection.

## Key Features
- **Scenario Profiles:** Automated setup for Open, WPA2, Hidden, and Misconfigured APs.
- **L7 Services:** Automated deployment of DNS, NTP, and HTTP services for realistic simulations.
- **Service Status:** Live monitoring panel and consistent cleanup routines.

---

## Implementation Archive
<details>
<summary>Click to view original Technical Specifications & Usage</summary>

### Wireless Access Point Toolkit (WAPT)
A modular, accessible command-line toolkit for launching simulated wireless access points to support wireless threat simulations and cyber security research.

### Table of Contents
- [Changelog](#changelog)

### Features
- Scenario-aligned AP profiles for 13 WATT threats (e.g. Evil Twin, Open Rogue, Misconfigured)
- Fully automated AP launch with no operator input required
- NAT forwarding and custom BSSID support
- Live Service Status panel
- Time-based status expiry and consistent cleanup
- Modular Bash/Python CLI integration
- Robust error handling and session logging
- Accessibility: multiple colour themes, high-contrast and monochrome modes, keyboard navigation

### Accessibility & Inclusivity
- Multiple colour themes: Dark, Light, High Contrast, Monochrome
- High-contrast and monochrome modes for low vision and colourblind users
- Fully keyboard-navigable menu system
- Clear, consistent prompts and colour cues throughout the UI
- Accessible to users with limited command-line experience

### Project Structure
```
/src/
├── python/
│   ├── wapt.py
│   └── logs/
│       └── wapt_session.log
├── bash/
│   ├── config/
│   ├── helpers/
│   ├── services/
│   └── utilities/
├── docs/
│   └── (Sphinx or other documentation)
```

### Requirements
- Linux host with support for hostapd, dnsmasq, iptables
- Wireless interface supporting AP mode (e.g. Alfa AWUS036ACM)
- Python 3.x

### Installation
1. Clone the repository
2. Install Python dependencies (if any)
3. Ensure required system packages are installed (hostapd, dnsmasq, iptables)

### Usage
```
cd src/python
python3 wapt.py
```
- Use the menu to select and launch AP profiles, manage services, or change themes.
- Session events are logged to `src/python/logs/wapt_session.log`.

### Access Point Profiles
| Profile         | Description                                   | Security   |
|-----------------|-----------------------------------------------|------------|
| T001            | Open Access Point                             | None       |
| T003            | Open, WPA2, Hidden, Misconfig                 | Mixed      |
| T004            | WPA2 Evil Twin                                | WPA2-PSK   |
| T005            | WPA2 + Open Rogue                             | WPA2/Open  |
| T006            | Misconfigured WPA1/TKIP                       | WPA1-TKIP  |
| T007, T009      | WPA2 for client targeting                     | WPA2-PSK   |
| T014–T016       | Open + Client for spoofing/MiTM               | None       |

Each profile launches with L7 services (DNS, NTP, HTTP) and consistent interface configuration.

### Session Logging
All user actions and errors are logged to `src/python/logs/wapt_session.log` with timestamps for audit and troubleshooting.

### Developer Documentation
- Code is fully documented with Google-style docstrings.
- See the `docs/` directory for Sphinx-generated developer documentation (if present).

---

## **Licence**
This project is licenced under the MIT Licence.

---

## **Author**
- Paul Smurthwaite  
- 12 March 2025  
- TM470-25B

</details>

---
## Project Ecosystem
*See the [Core Toolkit (WSTT)](https://github.com/paulsmurthwaite/wstt) for the main analysis engine.*