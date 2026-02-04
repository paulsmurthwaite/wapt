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
## Project Ecosystem
*See the [Core Toolkit (WSTT)](https://github.com/paulsmurthwaite/wstt) for the main analysis engine.*