import threading
from DataCollector import DataCollector
from Printer import Printer
from JSONRefreshTimer import JSONRefreshTimer
from CallsignRequester import CallsignRequester

__author__ = "Simon Heck"

if __name__ == "__main__":
    json_url = "https://data.vatsim.net/v3/vatsim-data.json"
    departure_airport = "KATL"
    data_collector = DataCollector(json_url, departure_airport)
    printer = Printer(data_collector)   
    
    json_refresh = JSONRefreshTimer(data_collector)
    callsign_requester = CallsignRequester(printer)

    # initial data grab
    data_collector.update_proposed_departures()
    
    # Main Thread: automatically printing new flight
    # thread1: Timer that updates datacollectors JSON (Might have to lock object on update)
    # thread2: listens for user inputs of strip requests

    # thread1:
    user_input_thread = threading.Thread(target=callsign_requester.request_callsign_from_user)
    # thread2:
    JSON_timer_thread = threading.Thread(target=json_refresh.start_refreshing)
    # main thread:
    automated_strip_printing = threading.Thread(target=printer.autoprint)
    
    # start all threads
    JSON_timer_thread.start()
    automated_strip_printing.start()
    user_input_thread.start()

          
## TODO
# What if flight plan amended
# GUI
# easier changing of airport Lat-Long Points
# add more graceful thread closure