# Wireless Access Point Toolkit (WAPT)

A modular, accessible command-line toolkit for launching simulated wireless access points to support wireless threat simulations and cyber security research.

## Table of Contents
- [Features](#features)
- [Accessibility & Inclusivity](#accessibility--inclusivity)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Access Point Profiles](#access-point-profiles)
- [Session Logging](#session-logging)
- [Developer Documentation](#developer-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Changelog](#changelog)

## Features
- Scenario-aligned AP profiles for 13 WATT threats (e.g. Evil Twin, Open Rogue, Misconfigured)
- Fully automated AP launch with no operator input required
- NAT forwarding and custom BSSID support
- Live Service Status panel
- Time-based status expiry and consistent cleanup
- Modular Bash/Python CLI integration
- Robust error handling and session logging
- Accessibility: multiple colour themes, high-contrast and monochrome modes, keyboard navigation

## Accessibility & Inclusivity
- Multiple colour themes: Dark, Light, High Contrast, Monochrome
- High-contrast and monochrome modes for low vision and colourblind users
- Fully keyboard-navigable menu system
- Clear, consistent prompts and colour cues throughout the UI
- Accessible to users with limited command-line experience

## Project Structure
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

## Requirements
- Linux host with support for hostapd, dnsmasq, iptables
- Wireless interface supporting AP mode (e.g. Alfa AWUS036ACM)
- Python 3.x

## Installation
1. Clone the repository
2. Install Python dependencies (if any)
3. Ensure required system packages are installed (hostapd, dnsmasq, iptables)

## Usage
```
cd src/python
python3 wapt.py
```
- Use the menu to select and launch AP profiles, manage services, or change themes.
- Session events are logged to `src/python/logs/wapt_session.log`.

## Access Point Profiles
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

## Session Logging
All user actions and errors are logged to `src/python/logs/wapt_session.log` with timestamps for audit and troubleshooting.

## Developer Documentation
- Code is fully documented with Google-style docstrings.
- See the `docs/` directory for Sphinx-generated developer documentation (if present).
- See CHANGELOG.md for release history.

## Contributing
Contributions are welcome! Please open an issue or pull request.

## License
[MIT License](LICENSE)

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for version history.
