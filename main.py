import requests
import json
import time
import zpl
import random
from zebra import Zebra
import threading

__author__ = "Simon Heck"

class DataCollector:

    def __init__(self, json_url, departure_airport) -> None:
        self.callsign_list = {}
        self.json_url = json_url
        self.departure_airport = departure_airport

    def update_proposed_departures(self):
        self.update_json(json_url)
        self.scan_pilots()

    def get_callsign_list(self):
        return self.callsign_list
    
    def add_pilot_to_dep_list(self, current_pilot):
            pilot_callsign = current_pilot['callsign'].upper()
            self.callsign_list[pilot_callsign] = current_pilot
    
    def get_callsign_data(self, callsign):
        return self.callsign_list.get(callsign)
    
    def in_geographical_region(self, airport:str, airplane_lat_long:tuple) -> bool:
        # Dict of the form: { airport ICAO : ((NW lat_long point),(SE lat_long point)) }
        airports = {
            "KATL" : ((33.66160132114376, -84.4567732450538),(33.61374004734878,-84.39639798954067)),
            "KCLT" : ((35.2323196840276,-80.97532070484328),(35.19812613679431,-80.92504772311364))
        }
        #KATL NW Lat_Long point
        nw_lat_long_point, se_lat_long_point = airports.get(airport)
        northern_latitude, western_longitude = nw_lat_long_point
        #KATL SE Lat_long point
        southern_latitude, eastern_longitude = se_lat_long_point
        # airplane lat_long position
        airplane_lat, airplane_long = airplane_lat_long
    
        if (airplane_lat < northern_latitude and airplane_lat > southern_latitude) and (airplane_long > western_longitude and airplane_long < eastern_longitude):
            return True

    def scan_pilots(self):
        connected_pilots = self.json_file['pilots']
        # Interpreting/Filtering JSON Data
        for i in range(len(connected_pilots)):
            # pilot at index i information
            current_pilot = connected_pilots[i]
            try:
                pilot_departure_airport = current_pilot['flight_plan']['departure']
                lat_long_tuple = (current_pilot['latitude'], current_pilot['longitude'])
                if pilot_departure_airport == self.departure_airport and self.in_geographical_region(self.departure_airport, lat_long_tuple):
                    # Save callsign of pilot and associated JSON Info
                    # to access, use: self.callsign_list.get(**callsign**)
                    # that will return the portion of the JSON with all of the pilot's info from when the system added them(flightplan, CID, etc.)
                    self.add_pilot_to_dep_list(current_pilot)
            except Exception as e:
                continue                

    def update_json(self, json_url):
        r = requests.get(json_url)
        self.json_file = r.json()
    
class Printer:
    def __init__(self, data_collector:DataCollector) -> None:
        self.data_collector = data_collector

    def input_callsign():
        callsign = input("Enter Callsign: ")
        return callsign.upper()

    def print_callsign_data(self, requested_callsign):
        # zebra = Zebra()
        # Q = zebra.getqueues()
        # zebra.setqueue(Q[0])
        callsign_data = self.data_collector.get_callsign_data(requested_callsign)
        if requested_callsign == "" or None:
            print("blank")
            # print blank strip
            # zebra.output(f"^XA^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS^FO0,972^GB203,4,4^FS^FO0,363^GB203,4,4^FS^FO0,242^GB203,4,4^FS^FO0,120^GB203,4,4^FS^FO66,0^GB4,365,4^FS^FO133,0^GB4,365,4^FS^FO133,1177^GB4,122,4^FS^FO66,1177^GB4,122,4^FS^FB140,1,0,L^FO5,1470^FD^A0b,40,40^FS^FB200,1,0,L^FO60,1400^FD^A0b,40,40^FS^FO130,1530^FD^A0b,40,40^FS^FO130,1320^BCB,40,N,N,N,A^FD^FS^FB200,1,0,R^FO45,1320^FD^A0b,80,80^FS^FO5,1200^FD^A0b,40,40^FS^FO80,1190^FD^A0b,40,40^FS^FO145,1220^FD^A0b,40,40^FS^FO5,1050^FD^A0b,40,40^FS^FB500,1,0,L^FO5,450^FD^A0b,40,40^FS^FB500,1,0,L^FO70,450^FD^A0b,40,40^FS^^FB500,1,0,L^FO135,450^FD^A0b,40,40^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ")
        
        elif callsign_data is not None:

            callsign = callsign_data['callsign']
            departure_airport = callsign_data['flight_plan']['departure']
            ac_type = callsign_data['flight_plan']['aircraft_faa']
            departure_time = f"P{callsign_data['flight_plan']['deptime']}"
            cruise_alt = self.format_cruise_altitude(callsign_data['flight_plan']['altitude'])
            flightplan = self.format_flightplan(callsign_data['flight_plan']['route'], departure_airport)
            assigned_sq = callsign_data['flight_plan']['assigned_transponder']
            destination = callsign_data['flight_plan']['arrival']
            remarks = callsign_data['flight_plan']['remarks']
            remarks = f"{remarks[:15]} ***"
            enroute_time = callsign_data['flight_plan']['enroute_time']
            cid = callsign_data['cid']
            exit_fix = self.match_ATL_exit_fix(flightplan)
            computer_id = self.generate_random_id()

            print(f"{callsign}, {departure_airport}, {ac_type}, {departure_time}, {cruise_alt}, {flightplan}, {assigned_sq}, {destination}, {enroute_time} {cid}, {exit_fix}, {computer_id}")
            #print flight strip on printer
            # zebra.output(f"^XA^CFC,40,40~TA000~JSN^LT0^MNN^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI27^PA0,1,1,0^XZ^XA^MMT^PW203^LL1624^LS-20^FO0,1297^GB203,4,4^FS^FO0,972^GB203,4,4^FS^FO0,363^GB203,4,4^FS^FO0,242^GB203,4,4^FS^FO0,120^GB203,4,4^FS^FO66,0^GB4,365,4^FS^FO133,0^GB4,365,4^FS^FO133,1177^GB4,122,4^FS^FO66,1177^GB4,122,4^FS^FB140,1,0,L^FO5,1470^FD{callsign}^A0b,40,40^FS^FB200,1,0,L^FO60,1400^FD{ac_type}^A0b,40,40^FS^FO130,1530^FD{computer_id}^A0b,40,40^FS^FO130,1320^BCB,40,N,N,N,A^FD{cid}^FS^FB200,1,0,R^FO45,1320^FD{exit_fix}^A0b,80,80^FS^FO5,1200^FD{assigned_sq}^A0b,40,40^FS^FO80,1190^FD{departure_time}^A0b,40,40^FS^FO145,1220^FD{cruise_alt}^A0b,40,40^FS^FO5,1050^FD{departure_airport}^A0b,40,40^FS^FB500,1,0,L^FO5,450^FD{flightplan}^A0b,40,40^FS^FB500,1,0,L^FO70,450^FD{destination}^A0b,40,40^FS^^FB500,1,0,L^FO135,450^FD{remarks}^A0b,40,40^FS^FO0,1175^GB203,4,4^FS^PQ1,0,1,Y^XZ")
        else:
            print(f"Could not find {requested_callsign} in ATL proposals. Loser.")

    def format_flightplan(self, flightplan:str, departure:str):

        flightplan.replace(".", " ")
        # split flightplan into a list of the routes waypoints
        flightplan_list = flightplan.split(' ')
        # remove any DCT's from the waypoint list
        if "DCT" in flightplan_list:
            flightplan_list.remove("DCT")
        if "dct" in flightplan_list:
            flightplan_list.remove("dct")
        # for i in range(len(flightplan_list)):
        #     if len(flightplan_list[i]) > 8:
        #         flightplan_list.pop(i)
        #         i -= 1
        i=0
        amended = False
        while(i < len(flightplan_list)):
            if len(flightplan_list[i]) > 6:
                flightplan_list.pop(i)
                amended = True
            else:
                i +=1
        
        # Truncates flightplan route to first 3 waypoints. routes longer than 3 waypoints are represented with a ./. at the end
        build_string = ""
        for i in range(len(flightplan_list)):
            if i >= 3:
                build_string = f"{build_string} ./."
                break
            build_string = f"{build_string} {flightplan_list[i]}"
        build_string = build_string.strip()
        flightplan = f"{departure} {build_string}"
        # if amended:
        #     flightplan = f"+{build_string}+"
        # else:
        #     flightplan = build_string

        return flightplan
    
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
        if len(flightplan_list) > 1:
            exit_fix = exit_fixes.get(flightplan_list[1][:5])
        if exit_fix is None:
            exit_fix = ""
        return exit_fix
    
    def generate_random_id(self):
        r1 = random.randint(0,9)
        r2 = random.randint(0,9)
        r3 = random.randint(0,9)
        return f"{r1}{r2}{r3}"
    
class JSONRefreshTimer:
    def __init__(self, data_collector:DataCollector) -> None:
        self.data_collector = data_collector
    def start_refreshing(self, delay:int = 10):
        while(True):            
            time.sleep(delay)
            self.data_collector.update_proposed_departures()

    # def restart(self, countdown_time: int):
    #     self.start_time = time.perf_counter()
    #     self.current_time = time.perf_counter()
    #     while((self.current_time - self.start_time) < countdown_time):
    #         self.current_time = time.perf_counter()
    #     return True

class CallsignRequester:
    def __init__(self, printer: Printer) -> None:
        self.printer = printer

    def request_callsign_from_user(self) -> str:
        while(True):
            callsign_to_print = input("Enter Callsign: ")
            callsign_to_print = callsign_to_print.upper()
            printer.print_callsign_data(callsign_to_print)
        
# def print_tester(printed_callsigns:list):

#     callsign_list = data_collector.get_callsign_list()
#     for callsign_to_print in callsign_list:
#         if callsign_to_print not in printed_callsigns:
#             printer.print_callsign_data(callsign_to_print)
#             printed_callsigns.append(callsign_to_print)

def autoprint():
    printed_callsigns = []
    while(True):
        callsign_list = data_collector.get_callsign_list()
        for callsign_to_print in callsign_list:
            if callsign_to_print not in printed_callsigns:
                printer.print_callsign_data(callsign_to_print)
                printed_callsigns.append(callsign_to_print)
        time.sleep(1)

if __name__ == "__main__":
    json_url = "https://data.vatsim.net/v3/vatsim-data.json"
    departure_airport = "KATL"
    data_collector = DataCollector(json_url, departure_airport)
    printer = Printer(data_collector)   
    
    json_refresh = JSONRefreshTimer(data_collector)
    callsign_requester = CallsignRequester(printer)

    # initial data grab
    data_collector.update_proposed_departures()
    
    # Main Thread: automatically printing new flight strips
    # thread1: Timer that updates datacollectors JSON (Might have to lock object on update)
    # thread2: listens for user inputs of strip requests

    # thread1:
    user_input_thread = threading.Thread(target=callsign_requester.request_callsign_from_user)
    # thread2:
    JSON_timer_thread = threading.Thread(target=json_refresh.start_refreshing)
    # main thread:
    automated_strip_printing = threading.Thread(target=autoprint)
    
    # start all threads
    JSON_timer_thread.start()
    automated_strip_printing.start()
    user_input_thread.start()

          
## TODO
# print blank strip
# button for printing
# What if flight plan ammended
# What if fight plan 
# Manual addition of flight strip (i.e type in callsign, get strip)
# Blank strip...?