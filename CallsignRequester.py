import Printer

__author__ = "Simon Heck"

class CallsignRequester:
    def __init__(self, printer: Printer) -> None:
        self.printer = printer

    def request_callsign_from_user(self) -> str:
        while(True):
            callsign_to_print = input("Enter Callsign: ")
            callsign_to_print = callsign_to_print.upper()
            self.printer.print_callsign_data(callsign_to_print)