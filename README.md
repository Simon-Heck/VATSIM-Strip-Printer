Version: Python 3.11.3
# Overview:
  * WIP flight progress strips for ZTL.
  * Code Author: Simon Heck (Simon-Heck)
  * Printer Technician: Joey Costello(JoeyTheDev1)
  * Technical Advisor: Zackaria B.

# TODO:
  * don't print barcode for A80 departures
  * PRINT SIGMENNNNNTS OR SOMETHIGN
  * Don't print VFR strips/Don't print amended VFR strips?
  * sync data refresh with VATSIM data refresh cycle
  * Expand functionality to any airport. Currently only supports KATL and KCLT
  * Add GUI elements to the program
  * Allow easier editing of Lat-Long points for defining geographical areas(adding more airports)
  * LAT/LONG information stored in a JSON. GUI supports ability to input LAT/Long points for new airports
  * Different settings that control different variables/things to be printed on the strip.
  * Does TDLS normally print strips?

# Completed:
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
  
