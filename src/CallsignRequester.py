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
            flag = "Print"
            #What are we doing with this? Depends on what position the guy is working, maybe?
            try:
                if self.control_area["type"] != "GC" and self.control_area["type"] != "LC": 
                    flag = "Print"
                    print(flag)
                else:
                    print("not ground OR local")
                    print(len(callsign_to_print) < 6)
                    print((callsign_to_print.replace("V","",1)).isnumeric())
                    print(callsign_to_print.isalnum())
                    if len(callsign_to_print) < 6: #If the callsign is less than 6 characters, it can NOT be a CID. Therefore, we're printing a flight strip.    
                        flag = "Print"                        
                        print("less than 6 chars")
                    elif (callsign_to_print.replace("V","",1)).isnumeric(): #We're checking to see if the callsign starts with a "V" to indicate "visual separation".
                        flag = "Scan"
                    elif callsign_to_print.isalnum(): #If the callsign has numbers AND letters, it can NOT be a CID. Therefore, we're printing a flight strip.
                        flag = "Print"


                if flag == "Print":
                    self.request_callsign(callsign_to_print)
                elif flag == "SCAN":
                    print("SCAN STRIP!")

                #If callsign, print strip
                #If not callsign, function changes depending on GND or TWR
                #If ground, check to see in and out time. What if an airplane despawns on the taxi out?
                #If TWR, check if theres a "V" preceding the CID (transmits "VISUAL SEPARATION" to A80). Also, STOP timer. 

            except:
                continue
    
    def request_callsign(self, callsign):
        callsign_to_print = callsign.upper()
        self.printer.print_callsign_data(self.data_collector.get_callsign_data(callsign_to_print), callsign_to_print, self.control_area)