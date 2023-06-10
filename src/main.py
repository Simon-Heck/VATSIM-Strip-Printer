import threading
import argparse
from DataCollector import DataCollector
from Printer import Printer
from JSONRefreshTimer import JSONRefreshTimer
from CallsignRequester import CallsignRequester
from ClearStoredCallsigns import ClearStoredCallsigns
import pickle
__author__ = "Simon Heck"

class Main():
    def __init__(self) -> None:
        
        json_url = "https://data.vatsim.net/v3/vatsim-data.json"
        # cached_callsign_path = "./cached_departures_that_have_been_printed"
        cached_callsign_path = "C:\\Users\\simon\\OneDrive\\Documents\\Coding Projects\\strip-data-collector\\src\\cached_departures_that_have_been_printed"
        departure_airport = "KATL"

        printed_callsigns = []
        printed_callsign_file = open(cached_callsign_path, "rb")
        current_callsigns_cached = pickle.load(printed_callsign_file)
        printed_callsign_file.close()

        print_all_departures = False
        while(True):
            try:
                response = input("Do you want to print all departures on the ground? Reply with a '1' for yes, '0' for no: ")
                print_all_departures = bool(int(response))
                if(print_all_departures):
                    response = input(f"ARE YOU SURE? THIS WILL PRINT EVERY AIRCRAFT ON THE GROUND! (There are {len(current_callsigns_cached)} strips stored...). Reply '1' for yes, '0' for no: ")
                    print_all_departures = bool(int(response))
                    
                if(print_all_departures):
                    
                    response = input(f"Oh boy, that's gonna be a lot of paper. Do you want to clear the {len(current_callsigns_cached)} cached strips? Reply '1' for yes, '0' for no: ")
                    current_callsigns_cached = []
                    clear_cache = bool(int(response))
                    if(clear_cache):
                        # pickles an empty list into the cached file
                        clear_callsigns = ClearStoredCallsigns(cached_callsign_path)
                    
                break
            except ValueError:
                print("Please input either a 1 or 0....IDIOT")

        # # load callsigns so that they are not printed
        # if not print_cached_departures:
        printed_callsigns = current_callsigns_cached
        
        printer = Printer() 
        data_collector = DataCollector(json_url, departure_airport, printer, printed_callsigns, cached_callsign_path)
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
# remove callsign that departs
# GUI
# easier changing of airport Lat-Long Points
# add more graceful thread closure
if __name__ == "__main__":
   main = Main()