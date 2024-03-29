Version: Python 3.11.3
# Overview:

  * WIP flight progress strips for [vZTL](https://ztlartcc.org), on the [VATSIM Network](https://vatsim.net). Independent project not sponsered by VATSIM
  * Code Author: Simon Heck [(Simon-Heck)](https://github.com/Simon-Heck)
  * Printer Technician: Joey Costello [(JoeyTheDev1)](https://github.com/JoeyTheDev1/)
  * Technical Advisor: Zack B)

# In Progress:
  * Electronic Flight Strip Transfer System (EFSTS) / Networking
  * Print all the memory aid things
  * Add more comments and documentation

# To do:
  * Make starting text prompts easier to understand
  * Don't print VFR strips/Don't print amended VFR strips?
  * sync data refresh with VATSIM data refresh cycle
  * Clean up Code for new airports. Add new airports. Store in JSON?
  * Add visual flag to scanner elements. Build network for scanner.
  * Add GUI elements to the program

# Features:
  * Barcode with pilot VATSIM CID on ATL strips (for strip scanning)
  * Truncates route to first 3 waypoints
  * Prints only remarks after RMK/
  * Multi-threaded to simultaneously listen for user input, update JSON data, and scan for new departures
  * Print Hazardous Weather Information
  * Log airport delays & limited logic to determine cause.
  * Others

# Hardware:
  * [ZebraZD410 Printer](https://www.zebra.com/us/en/products/spec-sheets/printers/desktop/zd410.html)
  * [1x8 Flight Strips](https://bocathermal.txdesign.com/thermal-general-admission-ticket/details/boca-flight-strip-1-x-8/)
  * Computer with [python](https://www.python.org/downloads/) 3.1 or greater
  * theres a certain font to install. i know its not hardware but this is a place holder


# How to Run:
  * Aquire the following modules:
```
pip install zpl
pip install zebra
pip install requests
```
Run python on [main.py](src/main.py). For example:
```
python main.py
```


# Commands:
 * Memoryaids - Prints several memory aids, including STOP and NO LUAW.
 * Times - Prints the current taxi times & associated callsigns.
 * Purge - Clears queue count for delay reporting
 * DROP (Callsign) - Removes cid from queue counter.