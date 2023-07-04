import threading
from DataCollector import DataCollector
from Printer import Printer
from JSONRefreshTimer import JSONRefreshTimer
from CallsignRequester import CallsignRequester
from ClearStoredCallsigns import ClearStoredCallsigns
import pickle
import json
from HazardousWX import WXRadio
from EFSTS import Scanner

__author__ = "Simon Heck"

class Main():
    def __init__(self) -> None:
        acft_json_path = "./data/acft_database.json"
        airports_path = "./data/airports.json"
        printerpositions_path = "./data/positions.json"

        json_url = "https://data.vatsim.net/v3/vatsim-data.json"
        sigmetJSON = "https://beta.aviationweather.gov/cgi-bin/data/airsigmet.php?format=json"
        cwasJSON = "https://api.weather.gov/aviation/cwsus/"
       
        cached_callsign_path = "./data/cached_departures_that_have_been_printed"

        # TODO: Handle empty pickle file


        #7/3 BEGIN
        
        # ----Open Printer Positions----
        printer_positions_file = open(printerpositions_path, 'rb')
        printer_positions = json.load(printer_positions_file)
        printer_positions_file.close()

        # ---Open Airports File-----
        airfields_file = open(airports_path, 'rb')
        airports = json.load(airfields_file)
        airfields_file.close()
        
        # ---Open Aircraft File-----
        acft_file = open(acft_json_path, 'rb')
        acft_dict = json.load(acft_file)
        acft_file.close()

        #7/3 END

        try:
            printed_callsign_file = open(cached_callsign_path, "rb")
            current_callsigns_cached = pickle.load(printed_callsign_file)
        except EOFError:
            current_callsigns_cached = printed_callsigns
            printed_callsign_file = open(cached_callsign_path, "wb")
            pickle.dump(printed_callsigns, printed_callsign_file)
        printed_callsign_file.close()

        print_all_departures = False
        control_area = ""
        printed_callsigns = []

        # TODO move this to it's own class
        print("Initializing setup...")

        # ---------Choose Facilty---------------
        print("Please select your control facility. Your choices are:")
        facilities = printer_positions["facilities"]
        for i in facilities:
            print(i)
        user_facility = input()
        user_facility = str(user_facility.upper())
        try:
            user_facility = facilities[user_facility]
        except:
            printerfacilitydefault = tuple((facilities.items()))
            print(f"I'm sorry, I can't seem to find {user_facility}. Setting your facility to{str(printerfacilitydefault[0][0])}, the default facility.")
            user_facility = facilities[printerfacilitydefault[0][0]]

        # -------Choose Position in Facility---------
        control_area = tuple((user_facility.items()))[0] #If this isn't here... it causes the datacollector to silently error ?
        if len(user_facility) > 1:
            print("Please select your control position.")
            print("Your choices include:")
            for i in user_facility:
                print(i)
            user_position = input()
            user_position = user_position.upper()
            try:
                control_area = user_facility[user_position]
            except:
                printerpositiondefault = tuple((user_facility.items()))
                print(f"I'm sorry, I can't seem to find {user_position}. Setting your position to {str(printerpositiondefault[0][0])}, the default position.")
                control_area = user_facility[printerpositiondefault[0][0]]
        else:
            print(f"Setting your position to {control_area[0]}.")
            printerpositiondefault = tuple((user_facility.items()))
            control_area = user_facility[printerpositiondefault[0][0]]

        # -----Print all Departures-----
        while(True):
            try:
                if control_area['auto_Print_Strips']: #If the position is configured to NOT auto-print strips... these settings are useless... so might as well skip 'em.
                    response = input("Do you want to print all departures on the ground? Reply with a '1' for yes, '0' for no: ")
                    print_all_departures = bool(int(response))
                    if(print_all_departures):
                        response = input(f"This will possibly print up to {len(current_callsigns_cached)} strips. Reply '1' for yes, '0' for no: ")
                        print_all_departures = bool(int(response))
                    
                if(print_all_departures):
                    response = input(f"Do you want to clear the {len(current_callsigns_cached)} cached strips? Reply '1' for yes, '0' for no: ")
                    current_callsigns_cached = []
                    clear_cache = bool(int(response))
                    if(clear_cache):
                        # pickles an empty list into the cached file
                        clear_callsigns = ClearStoredCallsigns(cached_callsign_path)
                break
            except ValueError:
                print("Please input either a 1 or 0....IDIOT")

        # load callsigns so that they are not printed
        # if not print_cached_departures:
        printed_callsigns = current_callsigns_cached
        
        printer = Printer(acft_dict) 
        data_collector = DataCollector(json_url, control_area, printer, printed_callsigns, cached_callsign_path, printer_positions, airports)
        efsts = Scanner(control_area, sigmetJSON, printer_positions, airports, data_collector)
        callsign_requester = CallsignRequester(printer, data_collector, control_area, efsts)
        json_refresh = JSONRefreshTimer(data_collector)
        wx_refresh = WXRadio(control_area, printer, airports, sigmetJSON, cwasJSON)


        # initial data grab
        data_collector.check_for_updates()

        # thread1: Timer that updates flightplan data when I new JSON is uploaded
        user_input = threading.Thread(target=callsign_requester.request_callsign_from_user)
        # thread2: listens for user inputs for strip requests
        JSON_timer = threading.Thread(target=json_refresh.start_refreshing)
        # Thread3: automatically prints new flight strips when callsign list updated
        automated_strip_printing = threading.Thread(target=data_collector.scan_for_new_aircraft_automatic)
        # Thread4: automatically print SIGMETs/AIRMETs every once in a while.
        wxradio = threading.Thread(target=wx_refresh.start_refreshing)
        # Thread5: Keep track of departure delays. Manage strip scanners.
        scans = threading.Thread(target=efsts.opsNet)


        print("Would you like Hazardous Weather Advisories?")
        enablewxradio = bool(int(input('Reply "1" for yes, and "0" for no: ')))


        #start printing strips while customer decides whether or not they want to sync the data.
        automated_strip_printing.start()

        # Sync pulling of data BEFORE starting threads
        print("Would you like to sync data collection with the network?")
        try:
            if bool(int(input('Reply "1" for yes, and "0" for no: '))):
                json_refresh.calculateDelay(json_url)
        except:
            print("Sorry, I'm not sure I understand. Skipping data sync.")

        # start other threads
        JSON_timer.start()
        user_input.start()
        if enablewxradio:
            wxradio.start()

        if control_area['type'] == "GC" or control_area['type'] == "LC":
            scans.start()

if __name__ == "__main__":
   main = Main()