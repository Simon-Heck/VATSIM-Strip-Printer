Version: Python 3.11.3
# Overview:
  * WIP flight progress strips for ZTL.
  * Code Author: Simon Heck (Simon-Heck)
  * Printer Technician: Joey Costello(JoeyTheDev1)
  * Technical Advisor: Zackaria B.

# TODO:
  * don't print barcode for A80 departures
  * Print Sigmets
  * Don't print VFR strips/Don't print amended VFR strips?
  * sync data refresh with VATSIM data refresh cycle
  * Clean up Code for new airports and adding new airports. Store in JSON?
  * Add GUI elements to the program

# Completed:
  * ~~Expand functionality to any airport. Currently only supports KATL and KCLT~~
  * ~~Handle edge cases: ie. During long event, pilot departs, but later reconnects with same callsign but different aircraft and flightplan. likely add logic to detect when stored callsign is airborne amd remove from list~~
  * ~~Add in amendment numbers and amended flightplans to strips~~

# How to Run
  * Install python 3.1 or greater
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
  
