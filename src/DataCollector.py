import requests
from Printer import Printer
import time
__author__ = "Simon Heck"

class DataCollector:

    def __init__(self, json_url:str, departure_airport:str, printer:Printer) -> None:
        self.callsign_list = {}
        self.json_url = json_url
        self.departure_airport = departure_airport
        self.printer = printer

    def check_for_updates(self):
        self.update_json(self.json_url)
        self.scan_pilots()

    def get_json(self):
        return self.json_file
    
    def get_callsign_list(self):
        return self.callsign_list
    
    def add_callsign_to_dep_list(self, pilot_callsign:str, pilot_associated_with_callsign:dict):
        # was callsign amended and was the callsign already in the departure list
        if pilot_callsign in self.callsign_list and pilot_associated_with_callsign['flight_plan']['route'] != self.callsign_list[pilot_callsign]['flight_plan']['route']:
            self.callsign_list[pilot_callsign] = pilot_associated_with_callsign
            self.printer.print_callsign_data(self.callsign_list[pilot_callsign], pilot_callsign)
        else:
            self.callsign_list[pilot_callsign] = pilot_associated_with_callsign

    def scan_for_new_aircraft_automatic(self):
        printed_callsigns = []
        while(True):
            callsign_table = self.get_callsign_list()
            for callsign_to_print in callsign_table:
                if callsign_to_print not in printed_callsigns:
                    self.printer.print_callsign_data(callsign_table.get(callsign_to_print), callsign_to_print)
                    printed_callsigns.append(callsign_to_print)
            time.sleep(0.5)

    def get_callsign_data(self, callsign) -> dict:
        if callsign not in self.callsign_list:
            return None
        else:
            return self.callsign_list.get(callsign)
    
    def in_geographical_region(self, airport:str, airplane_lat_long:tuple) -> bool:
        # Dict of the form: { airport ICAO : ((NW lat_long point),(SE lat_long point)) }
        airports = {
            "KATL" : ((33.66160132114376, -84.4567732450538),(33.61374004734878,-84.39639798954067)),
            "KCLT" : ((35.2323196840276,-80.97532070484328),(35.19812613679431,-80.92504772311364))
        }
        
        nw_lat_long_point, se_lat_long_point = airports.get(airport)
        #KATL NW Lat_Long point
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
                pilot_callsign = current_pilot['callsign'].upper()
                if pilot_departure_airport == self.departure_airport and self.in_geographical_region(self.departure_airport, lat_long_tuple):
                    # Save callsign of pilot and associated JSON Info
                    # to access, use: self.callsign_list.get(**callsign**)
                    # that will return the portion of the JSON with all of the pilot's info from when the system added them(flightplan, CID, etc.)
                    self.add_callsign_to_dep_list(pilot_callsign, current_pilot)
            except TypeError as te:
                pass        
            except Exception as e:
                print(e)  

    def update_json(self, json_url):
        r = requests.get(json_url)
        self.json_file = r.json()