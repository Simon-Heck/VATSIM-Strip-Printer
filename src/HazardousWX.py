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
    "KODX":(41.71323176607031, -98.96874170513782)
    }

### Yes, this has shit hard coded in. I don't feel like figuring out how to set up location search... yet.

class WXRadio:
    def start_refreshing(delay:int = 10):
        while(True):
            WXRadio.fetch_sigmet(sigmetJSON)
            #WXRadio.fetch_cwas(cwasJSON)
            time.sleep(delay)
            

    def fetch_sigmet(api):
        print("Playing fetch with the National Weather Service, in Peachtree City, GA.")
        print("Fetching SIGMETs for Atlanta GA, please wait!")
        r = requests.get(api)
        raw = r.json()
        # print(raw)
        for i in raw:
            isEligible = False
            #calculate if its reportable
            #print("NEW SIGMET")
            for u in i["coords"]:
                if i["airSigmetId"] not in sigmet_list: 
                    airport_lat, airport_lon = airports["KATL"]
                    sigmetlat, sigmetlon = u["lat"],u["lon"]
                    if ((sigmetlat - 1 < airport_lat < sigmetlat + 1) or (sigmetlon - 1 < airport_lon < sigmetlon + 1)):
                        isEligible = True
            if isEligible:
                hazard = i["hazard"]
                type = i["airSigmetType"]
                rawsigmet = i["rawAirSigmet"].splitlines()
                sigmet_list.append(i["airSigmetId"])
                if type == "SIGMET":
                    print(f'{rawsigmet[2]} {rawsigmet[3]}... {rawsigmet[4]}... {rawsigmet[6]}{rawsigmet[7]}')
                elif type == "AIRMET":
                    print(f'{rawsigmet[2]} {rawsigmet[3]} ')#{rawsigmet[6]}')


    
    def fetch_cwas(api):
        print("Playing fetch with the Center Weather Service Unit of ZTL.")
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
                print(f'This is {cwsu} center weather advisory {id} for {hazard}.')
                cwa_list.append(id)


WXRadio.start_refreshing()