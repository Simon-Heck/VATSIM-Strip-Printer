import requests
import json
import time
import zpl
import random
from zebra import Zebra

__author__ = "Simon Heck"

class DataCollector:

    def __init__(self, json_url) -> None:
        self.callsign_list = {}
        self.json_url = json_url
    def update_departure_list(self):
        self.update_json(json_url)
        self.scan_pilots()
    
    def add_pilot_to_dep_list(self, current_pilot):
            pilot_callsign = current_pilot['callsign'].upper()
            self.callsign_list[pilot_callsign] = current_pilot
    
    def get_callsign_data(self, callsign):
        return self.callsign_list.get(callsign)

    def scan_pilots(self):
        connected_pilots = self.json_file['pilots']
        # Interpreting/Filtering JSON Data
        for i in range(len(connected_pilots)):
            # pilot at index i information
            current_pilot = connected_pilots[i]
            try:
                departure_airport = current_pilot['flight_plan']['departure']
                if departure_airport == "KATL":
                    # Save callsign of pilot and associated JSON Info
                    # to access, use: self.callsign_list.get(**callsign**)
                    # that will return the portion of the JSON with all of the pilot's info from when the system added them(flightplan, CID, etc.)
                    self.add_pilot_to_dep_list(current_pilot)
            except Exception as e:
                continue                

    def print_strip(callsign):
        """
        Print strip for specific callsign
        """
        # TODO
        # strip printer code here including formatting

    def update_json(self, json_url):
        r = requests.get(json_url)
        self.json_file = r.json()
        # return r.json()
    
class Printer:
    def __init__(self, data_collector:DataCollector) -> None:
        self.data_collector = data_collector

    def input_callsign():
        callsign = input("Enter Callsign: ")
        return callsign.upper()
        # try:
        # _thread.start_new_thread(self.start_timer,("timer thread", 0,))
        # _thread.start_new_thread(self.print_callsign_data,("printing tread", 0,))
        # except:
            # print("unable to start thread")
        #  self.start_timer()
        #  self.print_callsign_data()
            
    # def start_timer(self, thread_name, delay):
    #     print("hi")
    #     self.start_time = time.perf_counter()
    #     while(True):
    #         self.current_time = time.perf_counter()
    #         if (self.current_time-self.start_time) >= 15:
    #             print("I am a clock that counted 15 seconds, i am cool")
    #         #   self.dataCollector.update_json(self.json_url)
    #         #   self.dataCollector.scan_pilots()

    def print_callsign_data(self, requested_callsign):
        callsign_data = self.data_collector.get_callsign_data(requested_callsign)

        if callsign_data is not None:

            callsign = callsign_data['callsign']
            ac_type = callsign_data['flight_plan']['aircraft_faa']
            departure_time = f"P{callsign_data['flight_plan']['deptime']}"
            cruise_alt = self.format_cruise_altitude(callsign_data['flight_plan']['altitude'])
            flightplan = self.format_flightplan(callsign_data['flight_plan']['route'])
            assigned_sq = callsign_data['flight_plan']['assigned_transponder']
            destination = callsign_data['flight_plan']['arrival']
            remarks = callsign_data['flight_plan']['remarks']
            remarks = f"{remarks[:15]} ***"
            enroute_time = callsign_data['flight_plan']['enroute_time']
            cid = callsign_data['cid']
            exit_fix = self.match_ATL_exit_fix(flightplan)
            computer_id = self.generate_random_id()

            print(f"{callsign}, {ac_type}, {departure_time}, {cruise_alt}, {flightplan}, {assigned_sq}, {destination}, {enroute_time} {cid}, {exit_fix}, {computer_id}")
            #print flight strip on printer
            # zebra = Zebra()
            # Q = zebra.getqueues()
            # zebra.setqueue(Q[0])
            # zebra.output(f"^XA^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS^FO0,972^GB203,4,4^FS^FO0,363^GB203,4,4^FS^FO0,242^GB203,4,4^FS^FO0,120^GB203,4,4^FS^FO66,0^GB4,365,4^FS^FO133,0^GB4,365,4^FS^FO133,1177^GB4,122,4^FS^FO66,1177^GB4,122,4^FS^FB140,1,0,L^FO5,1470^FD{callsign}^A0b,40,40^FS^FB200,1,0,L^FO60,1400^FD{ac_type}^A0b,40,40^FS^FO130,1530^FD{computer_id}^A0b,40,40^FS^FO130,1320^BCB,40,N,N,N,A^FD{cid}^FS^FB200,1,0,R^FO45,1320^FD{exit_fix}^A0b,80,80^FS^FO5,1200^FD{assigned_sq}^A0b,40,40^FS^FO80,1190^FD{departure_time}^A0b,40,40^FS^FO145,1220^FD{cruise_alt}^A0b,40,40^FS^FO5,1050^FDKATL^A0b,40,40^FS^FB500,1,0,L^FO5,450^FD{flightplan}^A0b,40,40^FS^FB500,1,0,L^FO70,450^FD{destination}^A0b,40,40^FS^^FB500,1,0,L^FO135,450^FD{remarks}^A0b,40,40^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ")
        else:
            print(f"could not find {callsign} in ATL proposals")

    def format_flightplan(self, flightplan):
        
        # split flightplan into a list of the routes waypoints
        flightplan_list = flightplan.split(' ')
        # remove any DCT's from the waypoint list
        if "DCT" in flightplan_list:
            flightplan_list.remove("DCT")
        if "dct" in flightplan_list:
            flightplan_list.remove("dct")
        # Truncates flightplan route to first 3 waypoints. routes longer than 3 waypoints are represented with a ./.
        build_string = ""
        for i in range(len(flightplan_list)):
            if i >= 3:
                build_string = f"{build_string} ./."
                break
            build_string = f"{build_string} {flightplan_list[i]}"
        flightplan = build_string

        return flightplan.strip()
    
    def format_cruise_altitude(self, altitude):
        formatted_altitude = altitude[:-2]
        if len(formatted_altitude) < 2:
            formatted_altitude = f"00{formatted_altitude}"
        elif len(formatted_altitude) < 3:
            formatted_altitude = f"0{formatted_altitude}"
        return formatted_altitude
    
    def match_ATL_exit_fix(self, flightplan):
        exit_fixes={
            "NOONE" : "N1",
            "NOTWO" : "N2",
            "EAONE" : "E1",
            "EATWO" : "E2",
            "SOONE" : "S1",
            "SOTWO" : "S2",
            "WEONE" : "W1",
            "WETWO" : "W2",
            "PENCL" : "N3",
            "VARNM" : "N5",
            "PADGT" : "N4",
            "SMKEY" : "N6",
            "PLMMR" : "E3",
            "JACCC" : "E5",
            "PHIIL" : "E4",
            "GAIRY" : "E6",
            "VRSTY" : "S3",
            "SMLTZ" : "S5",
            "BANNG" : "S4",
            "HAALO" : "S6",
            "POUNC" : "W3",
            "KAJIN" : "W5",
            "NASSA" : "W4",
            "CUTTN" : "W6"
        }
        exit_fix = ""
        flightplan_list = flightplan.split(" ")
        if len(flightplan_list) > 0:
            exit_fix = exit_fixes.get(flightplan_list[0][:5])
        if exit_fix is None:
            exit_fix = ""
        return exit_fix
    
    def generate_random_id(self):
        r1 = random.randint(0,9)
        r2 = random.randint(0,9)
        r3 = random.randint(0,9)
        return f"{r1}{r2}{r3}"
if __name__ == "__main__":
    json_url = "https://data.vatsim.net/v3/vatsim-data.json"
    data_collector = DataCollector(json_url)
    printer = Printer(data_collector)   
    data_collector.update_departure_list()

    while(True):
        callsign = input("Enter Callsign: ")
        callsign = callsign.upper()
        printer.print_callsign_data(callsign)
          

## TODO
# button for printing
# What if flight plan ammended
# What if fight plan 
# Manual addition of flight strip (i.e type in callsign, get strip)
# Blank strip...?
        
        # def time_elapsed(self) -> float:
        #      return self.current_time-self.start_time
        
        # def reset_timer(self):
        #      self.start_time = self.current_time

# class UserInput:
#      def __init__(self) -> None:
#           pass
#      def get_input():
#           return input("Enter Callsign: ")
             
# def main(): 
    #Getting JSON Data
    # json_url = "https://data.vatsim.net/v3/vatsim-data.json"
    # dataCollector = DataCollector(json_url)
    # timer = Timer()
    # user_input = UserInput()

    # try:
    #     thread.start_new_thread(timer.start_timer())
    # # peak coding right here
    # start_time = time.perf_counter()
    # # print("hi")
    # while(True):
    #     current_time = time.perf_counter()
    #     if (current_time - start_time) >= 15:
    #         print("wow, that was 15 seconds")
    #         dataCollector.update_json(json_url)
    #         dataCollector.scan_pilots()
    #         start_time = current_time

# if __name__ == "main":







# for pilots in connected_pilots:
#     pilot_dep = pilots[['flight_plan']['departure']]
#     if pilot_dep == "KATL":
#      print(pilot_dep)

#for x in cont['pilots']:
#    if ['flight_plan'] != None:
#        havePlans = x

#for k in havePlans['flight_plan']:
#    if ['departure'] == "KATL":
#        print("fuck")
    
