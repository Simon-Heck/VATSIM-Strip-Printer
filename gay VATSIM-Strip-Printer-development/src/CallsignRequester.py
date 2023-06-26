from Printer import Printer
from DataCollector import DataCollector
import time

__author__ = "Simon Heck"

class CallsignRequester:
    control_area = "A80ALL" # Set A80ALL as the control area in case theres some failure, lol.
    def __init__(self, printer: Printer, data_collector: DataCollector, control_area) -> None:
        self.printer = printer
        self.data_collector = data_collector
        self.control_area = control_area
    def request_callsign_from_user(self) -> str:
        time.sleep(0.5)
        while(True):
            callsign_to_print = input("Enter Callsign: ")
            self.request_callsign(callsign_to_print)
    
    def request_callsign(self, callsign):
        callsign_to_print = callsign.upper()
        self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print, self.control_area)