from Printer import Printer
from DataCollector import DataCollector
import time
from EFSTS import Scanner

__author__ = "Simon Heck"

class CallsignRequester:
    control_area = "A80ALL" # Set A80ALL as the control area in case theres some failure, lol.
    def __init__(self, printer: Printer, data_collector: DataCollector, control_area, scanner: Scanner) -> None:
        self.printer = printer
        self.data_collector = data_collector
        self.control_area = control_area
        self.scan = scanner

    def request_callsign_from_user(self) -> str:
        time.sleep(0.5)
        while(True):
            callsign_to_print = input("Enter Callsign: ")

            #Figure out what to do with the inputted value.
            flag = self.determineFlag(callsign_to_print.upper())

            #Process inputted value accordingly.
            if flag == "Print":
                self.request_callsign(callsign_to_print)
            elif flag == "Scan":
                self.scan.scan(callsign_to_print)
            elif flag == "TEST":
                self.printer.print_memoryAids()
            elif flag == "PURGE":
                self.scan.purgeQueue()
            elif flag == "TIME":
                self.scan.listTimes()
    
    def request_callsign(self, callsign):
        callsign_to_print = callsign.upper()
        self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print, self.control_area)

    def determineFlag(self,callsign_to_print):
        flag = "Print"
        Visual = False
        #Detect if this is to print memory aids
        if callsign_to_print.lower() == "memoryaids":
            return "TEST"
        if callsign_to_print.lower() == "purge":
            return "PURGE"
        if callsign_to_print.lower() == "times":
            return "TIME"

        #What are we doing with this? Depends on what position the guy is working, maybe?
        #If they're NOT working Ground or Local, they shouldn't be scanning strips.
        if self.control_area["type"] != "GC" and self.control_area["type"] != "LC": 
            return "Print"
        else:
            if len(callsign_to_print) < 6: #If the callsign is less than 6 characters, it can NOT be a CID. Therefore, we're printing a flight strip.    
                return "Print"               
            elif (callsign_to_print.upper().replace("V","",1)).isnumeric(): #We're checking to see if the callsign starts with a "V" to indicate "visual separation".
                #TODO: Add functionality to detect if visual separation is being applied.
                return "Scan"
            elif callsign_to_print.isalnum(): #If the callsign has numbers AND letters, it can NOT be a CID. Therefore, we're printing a flight strip.
                return "Print"
            else:
                return flag

            #If callsign, print strip
            #If not callsign, function changes depending on GND or TWR
            #If ground, check to see in and out time. What if an airplane despawns on the taxi out?
            #If TWR, check if theres a "V" preceding the CID (transmits "VISUAL SEPARATION" to A80). Also, STOP timer. 