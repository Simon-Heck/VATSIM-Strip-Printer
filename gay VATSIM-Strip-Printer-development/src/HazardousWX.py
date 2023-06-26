import time
#import json
import requests
#import re
from Printer import Printer
from DataCollector import control_areas

__author__ = "Simon Heck"


sigmet_list = [] 
cwa_list = []  
airports = open("./data/airports.json")

sigmetJSON = "https://beta.aviationweather.gov/cgi-bin/data/airsigmet.php?format=json"
cwasJSON = "https://api.weather.gov/aviation/cwsus/ZTL/cwas"
jurisdictionPath = control_areas
airportsPath = airports


### Yes, this has shit hard coded in. I don't feel like figuring out how to set up location search... yet.

class WXRadio:
    def __init__(self, control_area) -> None:
        self.control_area = control_area["airports"]
        pass

    def start_refreshing(self, delay:int = 300):
        while(True):
            self.fetch_sigmet(sigmetJSON, self.control_area)
            self.fetch_cwas(cwasJSON, self.control_area)
            time.sleep(delay)
            

    def fetch_sigmet(self, api, control_area):
        r = requests.get(api)
        raw = r.json()
        # print(raw)
        for i in raw:
            isEligible = False
            #calculate if its reportable
            for u in i["coords"]:
                if i["airSigmetId"] not in sigmet_list:
                    for fieldlist in control_area:
                        try:
                            airport_lat, airport_lon = airportsPath[fieldlist]
                            sigmetlat, sigmetlon = u["lat"],u["lon"]
                            if ((sigmetlat - .8333 < airport_lat < sigmetlat + .8333) and (sigmetlon - .8333 < airport_lon < sigmetlon + .8333)):
                                isEligible = True
                        except:
                            return
            if isEligible:
                hazard = i["hazard"]
                type = i["airSigmetType"]
                rawsigmet = i["rawAirSigmet"].splitlines()
                sigmet_list.append(i["airSigmetId"])
                if type == "SIGMET":
                #    print(f'GI G1 {rawsigmet[2]} {rawsigmet[3]}... {rawsigmet[4]}... {rawsigmet[6]}{rawsigmet[7]} ...ZTLFD')
                    Printer.print_gi_messages(f'G1 {rawsigmet[2]} {rawsigmet[3]}... {rawsigmet[4]}... {rawsigmet[6]}{rawsigmet[7]} ...ZTLFD')
                elif type == "AIRMET":
                #    print(f'GI G1 {rawsigmet[2]} {rawsigmet[3]} {rawsigmet[6]} ...ZTLFD')
                    gi_message = (f'G1 {rawsigmet[2]} {rawsigmet[3]} {rawsigmet[6]} ...ZTLFD')
                    Printer.print_gi_messages(gi_message)
    
    def fetch_cwas(self, api, control_area):
        r = requests.get(api)
        raw = r.json()
        # print(raw)
        for i in raw["features"]:
            id = i["properties"]["sequence"]
            advzy = i["properties"]
            if id not in cwa_list:
                #print(["cwsu"])
                cwsu = advzy['cwsu']
                hazard = advzy["text"]
                # print(f'GI G1 {cwsu} CWA {id} for {hazard}.')
                gi_message = f'G1 {cwsu} CWA {id} for {hazard} ...ZTLFD'
                Printer.print_gi_messages(gi_message)
                cwa_list.append(id)