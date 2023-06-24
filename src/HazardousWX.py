import time
import json
import requests
import re

__author__ = "Simon Heck"

sigmetJSON = "https://beta.aviationweather.gov/cgi-bin/data/airsigmet.php?format=json"
cwasJSON = "https://api.weather.gov/aviation/cwsus/ZTL/cwas"

sigmet_list = [] 
cwa_list = []  
airports = {
    "KATL":(33.63734349729365, -84.42911583827573),
    "KODX":(41.71323176607031, -98.96874170513782),
    "KTKE":(41.765013127151114, -96.17884464621223),
    "KAFK":(40.60583096912623, -95.86428467726931),
    "KMRS":(41.4303195521458, -88.42153437224778)
    }

### Yes, this has shit hard coded in. I don't feel like figuring out how to set up location search... yet.

class WXRadio:
    def __init__(self) -> None:
        pass

    def start_refreshing(self,delay:int = 300):
        while(True):
            self.fetch_sigmet(sigmetJSON)
            self.fetch_cwas(cwasJSON)
            time.sleep(delay)
            

    def fetch_sigmet(self, api):
        r = requests.get(api)
        raw = r.json()
        # print(raw)
        for i in raw:
            isEligible = False
            #calculate if its reportable
            for u in i["coords"]:
                if i["airSigmetId"] not in sigmet_list: 
                    airport_lat, airport_lon = airports["KMRS"]
                    sigmetlat, sigmetlon = u["lat"],u["lon"]
                    if ((sigmetlat - .8333 < airport_lat < sigmetlat + .8333) and (sigmetlon - .8333 < airport_lon < sigmetlon + .8333)):
                        isEligible = True
            if isEligible:
                hazard = i["hazard"]
                type = i["airSigmetType"]
                rawsigmet = i["rawAirSigmet"].splitlines()
                sigmet_list.append(i["airSigmetId"])
                if type == "SIGMET":
                    print(f'GI G1 {rawsigmet[2]} {rawsigmet[3]}... {rawsigmet[4]}... {rawsigmet[6]}{rawsigmet[7]} ...ZTLFD')
                elif type == "AIRMET":
                    print(f'GI G1 {rawsigmet[2]} {rawsigmet[3]} {rawsigmet[6]} ...ZTLFD')
    
    def fetch_cwas(self, api):
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
                print(f'GI G1 {cwsu} CWA {id} for {hazard}.')
                cwa_list.append(id)