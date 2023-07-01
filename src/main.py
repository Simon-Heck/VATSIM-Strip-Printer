import threading
from DataCollector import DataCollector
from Printer import Printer
from JSONRefreshTimer import JSONRefreshTimer
from CallsignRequester import CallsignRequester
from ClearStoredCallsigns import ClearStoredCallsigns
import pickle
import json
from HazardousWX import WXRadio

__author__ = "Simon Heck"

class Main():
    def __init__(self) -> None:
        
        acft_json = "./data/acft_database.json"
        airports = "./data/airports.json"
        printerpositions = "./data/positions.json"

        json_url = "https://data.vatsim.net/v3/vatsim-data.json"
        sigmetJSON = "https://beta.aviationweather.gov/cgi-bin/data/airsigmet.php?format=json"
        cwasJSON = "https://api.weather.gov/aviation/cwsus/"
       
        cached_callsign_path = "./data/cached_departures_that_have_been_printed"
        # Full path used for debugging
        # cached_callsign_path = "C:\\Users\\simon\\OneDrive\\Documents\\Coding Projects\\strip-data-collector\\src\\cached_departures_that_have_been_printed"
        
        # departure_airport = "KATL"
        control_area = ""        
        printed_callsigns = []
        # TODO: Handle empty pickle file

        try:
            printed_callsign_file = open(cached_callsign_path, "rb")
            current_callsigns_cached = pickle.load(printed_callsign_file)
        except EOFError:
            current_callsigns_cached = printed_callsigns
            printed_callsign_file = open(cached_callsign_path, "wb")
            pickle.dump(printed_callsigns, printed_callsign_file)
        printed_callsign_file.close()

        print_all_departures = False
        while(True):
            #Load facility choices from positions.json
            print("Initializing setup...")
            print("Please select your control facility. Your choices are:")
            facilities = (json.load(open(printerpositions)))["facilities"]
            for i in facilities:
                print(i)
            facility = input()
            facility = str(facility.upper())
            try:
                facility = facilities[facility]
            except:
                printerfacilitydefault = tuple((facilities.items()))
                print("I'm sorry, I can't seem to find " + facility + ". Setting your facility to " + str(printerfacilitydefault[0][0]) + ", the default facility.")
                facility = facilities[printerfacilitydefault[0][0]]

            #Load position choices.
            control_area = tuple((facility.items()))[0] #If this isn't here... it causes the datacollector to silently error ?
            if len(facility) > 1:
                print("Please select your control position.")
                print("Your choices include:")
                for i in facility:
                    print(i)
                position = input()
                position = position.upper()
                try:
                    control_area = facility[position]
                except:
                    printerpositiondefault = tuple((facility.items()))
                    print("I'm sorry, I can't seem to find " + position + ". Setting your position to " + str(printerpositiondefault[0][0]) + ", the default position.")
                    control_area = facility[printerpositiondefault[0][0]]
            else:
                print(f"Setting your position to {control_area[0]}.")
                printerpositiondefault = tuple((facility.items()))
                control_area = facility[printerpositiondefault[0][0]]
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
        
        printer = Printer(acft_json) 
        data_collector = DataCollector(json_url, control_area, printer, printed_callsigns, cached_callsign_path)
        callsign_requester = CallsignRequester(printer, data_collector, control_area)
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


if __name__ == "__main__":
   main = Main()