import requests
from Printer import Printer
import time
import pickle
__author__ = "Simon Heck"

class DataCollector:

    def __init__(self, json_url:str, departure_airport:str, printer:Printer, cached_printed_departures:list, cached_departures_file_path:str) -> None:
        self.callsign_list = {}
        self.json_url = json_url
        self.departure_airport = departure_airport
        self.printer = printer
        self.printed_callsigns = cached_printed_departures
        self.cached_departures_file_path = cached_departures_file_path

    def check_for_updates(self):
        self.update_json(self.json_url)
        self.scan_pilots()

    def get_json(self):
        return self.json_file
    
    def get_callsign_list(self):
        return self.callsign_list
    
    def add_callsign_to_dep_list(self, pilot_callsign:str, pilot_associated_with_callsign:dict):
        # was callsign's route amended and is the callsign already in the departure list
        if pilot_callsign in self.callsign_list and pilot_associated_with_callsign['flight_plan']['route'] != self.callsign_list[pilot_callsign]['flight_plan']['route']:
            self.callsign_list[pilot_callsign] = pilot_associated_with_callsign
            self.printer.print_callsign_data(self.callsign_list[pilot_callsign], pilot_callsign)
        else:
            self.callsign_list[pilot_callsign] = pilot_associated_with_callsign

    def scan_for_new_aircraft_automatic(self):
        
        while(True):
            callsign_table = self.get_callsign_list()
            for callsign_to_print in callsign_table:
                if callsign_to_print not in self.printed_callsigns:
                    self.printer.print_callsign_data(callsign_table.get(callsign_to_print), callsign_to_print)
                    self.printed_callsigns.append(callsign_to_print)
                # auto_update cached callsigns
            file = open(self.cached_departures_file_path, 'wb')
            pickle.dump(self.printed_callsigns, file)
            file.close()
            time.sleep(1)

    def get_callsign_data(self, callsign) -> dict:
        if callsign not in self.callsign_list:
            return None
        else:
            return self.callsign_list.get(callsign)
    
    def in_geographical_region(self, airport:str, airplane_lat_long:tuple) -> bool:
        # Dict of the form: { airport ICAO : ((NW lat_long point),(SE lat_long point))}
        airports = {
        "KATL" : ((33.66160132114376, -84.4567732450538),(33.61374004734878,-84.39639798954067)),
        "KCLT" : ((35.2323196840276,-80.97532070484328),(35.19812613679431,-80.92504772311364)),
        # A80 Satellite Fields:
            "KPDK" : ((33.88584377733848, -84.31037981332257),(33.86777939460844, -84.29467279840003)),
            "KAHN" : ((33.9540766285094, -83.34223955210349),(33.940868873503796, -83.31558912314766)),
            "KFTY" : ((33.78279814861325, -84.53293817967267),(33.76835092467223, -84.5060731738479)),
            "KRYY" : ((34.01806592382934, -84.60951066352965),(34.00856797197957, -84.58389020270525)),
            "KMGE" : ((33.92439571872648, -84.539492361338),(33.90719431974648, -84.49717783156599)),
            "KLZU" : ((33.981190473249285, -83.97486176323365),(33.974784696390905, -83.94932713309667)),
            "KMCN" : ((32.706494713728155, -83.66622624254232),(32.683597342023745, -83.6330955963877)),
            "KWRB" : ((32.6574423721327, -83.60992131083712),(32.62137642781735, -83.56528935231016)),
            "KCSG" : ((32.524008383601796, -84.95611675437499),(32.509569501200396, -84.92453106069459)),
            "KLSF" : ((32.35285359752097, -85.00750196621792),(32.32036460057268, -84.97119558456957)),
        "KAGS" : ((33.38431894042706, -81.9800361075031),(33.360199147953026, -81.94780668360094)),
        "KAVL" : ((35.45024496074822, -82.55072847568015),(35.424125846590464, -82.53197447001651)),
        "KBHM" : ((33.57413878244034, -86.77696067339015),(33.55296874381666, -86.7306121011445)),
        "KTCL" : ((33.2352025266994, -87.62654866926034),(33.20439869303448, -87.60037030895185)),
        "KCHA" : ((35.049261224859045, -85.21148842212565),(35.02065794468386, -85.19363563873289)),
        "KGSO" : ((36.11934448224124, -79.96366556161747),(36.08009205818057, -79.91208131721585)),
        "KINT" : ((36.14600883289731, -80.2348108323373),(36.12254399263099, -80.20949077904496)),
        "KGSP" : ((34.91283847558762, -82.2342604646281),(34.874541090867005, -82.20606508317479)),
        "KGMU" : ((34.856977303456674, -82.36052424358789),(34.839825554426774, -82.34425932792081)),
        "KGYH" : ((34.76976667242393, -82.39198919030697),(34.74138327443452, -82.3592447823220)),
        "KHKY" : ((35.75033407939169, -81.40012291269115),(35.73511242544853, -81.3786437826562)),
        "KJQF" : ((35.40646408870109, -80.7152695290194),(35.376534270098354, -80.705334626720)),
        "KVUJ" : ((35.42452175090049, -80.16033764123814),(35.40539042674286, -80.138536646096)),
        "KMGM" : ((32.31006277880906, -86.41273587533833),(32.29159912500093, -86.37733071590472)),
        "KMXF" : ((32.39753740124293, -86.37726903604599),(32.367493083504456, -86.35182023661655)),
        "KTRI" : ((36.48772000522447, -82.42556968501692),(36.46038860112367, -82.39218154680279)),
        "KTYS" : ((35.824848376007616, -84.01527157210842),(35.79672807375963, -83.97553196286273))
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
                elif (pilot_departure_airport == self.departure_airport) and (not self.in_geographical_region(self.departure_airport, lat_long_tuple)) and (pilot_callsign in self.callsign_list):
                    self.remove_callsign_from_lists(pilot_callsign)
            except TypeError as e1:
                pass        
            except Exception as e2:
                print(e2)  

    def remove_callsign_from_lists(self, callsign_to_remove):
        self.callsign_list.pop(callsign_to_remove)
        self.printed_callsigns.pop(callsign_to_remove)

    def update_json(self, json_url):
        r = requests.get(json_url)
        self.json_file = r.json()