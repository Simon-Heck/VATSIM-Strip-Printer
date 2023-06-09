import threading
import argparse
from DataCollector import DataCollector
from Printer import Printer
from JSONRefreshTimer import JSONRefreshTimer
from CallsignRequester import CallsignRequester

__author__ = "Simon Heck"

class Main():
    def __init__(self) -> None:
        json_url = "https://data.vatsim.net/v3/vatsim-data.json"
        departure_airport = "KATL"
        
        printer = Printer() 
        data_collector = DataCollector(json_url, departure_airport, printer)
        callsign_requester = CallsignRequester(printer, data_collector)
        json_refresh = JSONRefreshTimer(data_collector)

        # initial data grab
        data_collector.check_for_updates()

        # thread1: Timer that updates flightplan data when I new JSON is uploaded
        user_input = threading.Thread(target=callsign_requester.request_callsign_from_user)
        # thread2: listens for user inputs for strip requests
        JSON_timer = threading.Thread(target=json_refresh.start_refreshing)
        # Thread3: automatically prints new flight strips when callsign list updated
        automated_strip_printing = threading.Thread(target=data_collector.scan_for_new_aircraft_automatic)
        
        # start all threads
        JSON_timer.start()
        automated_strip_printing.start()
        user_input.start()

## TODO
# GUI
# easier changing of airport Lat-Long Points
# add more graceful thread closure
if __name__ == "__main__":
   main = Main()