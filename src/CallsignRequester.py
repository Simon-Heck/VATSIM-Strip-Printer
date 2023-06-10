from Printer import Printer
from DataCollector import DataCollector
import time

__author__ = "Simon Heck"

class CallsignRequester:
    def __init__(self, printer: Printer, data_collector: DataCollector) -> None:
        self.printer = printer
        self.data_collector = data_collector
    def request_callsign_from_user(self) -> str:
        time.sleep(0.5)
        while(True):
            callsign_to_print = input("Enter Callsign: ")
            self.request_callsign(callsign_to_print)
    
    def request_callsign(self, callsign):
        callsign_to_print = callsign.upper()
        self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print)