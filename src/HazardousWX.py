import time
import json
import requests
from Printer import Printer

__author__ = "Zackaria Bomenir"

class WXRadio:
    def __init__(self, control_area, printer:Printer, airports, sigmetJSON, cwasJSON) -> None:
        self.sigmet_list = []
        self.cwa_list = []  
        self.airports = airports
        self.sigmetJSON = sigmetJSON
        self.cwasJSON = cwasJSON
        self.airportsPath = json.load(open(airports))['airfields']
        self.control_area = []
        self.control_area = control_area
        self.printer = printer

    def start_refreshing(self, delay:int = 300):
        self.fetch_sigmet(self.sigmetJSON, self.control_area["airports"])
        self.fetch_cwas(self.cwasJSON, self.airportsPath[self.control_area["airports"][0]]["ARTCC"])
        time.sleep(self.wxsync())
        while(True):
            self.fetch_sigmet(self.sigmetJSON, self.control_area["airports"])
            self.fetch_cwas(self.cwasJSON, self.airportsPath[self.control_area["airports"][0]]["ARTCC"])
            time.sleep(delay)
            

    def fetch_sigmet(self, api, control_area):
        r = requests.get(api)
        raw = r.json()
        # print(raw)
        for i in raw:
            isEligible = False
            #calculate if its reportable
            siglat = []
            siglon = []
            for u in i["coords"]:
                siglat.append(u["lat"])
                siglon.append(u["lon"])
            
            for u in i["coords"]:
                if i["airSigmetId"] not in self.sigmet_list:
                    for fieldlist in control_area:
                        try:
                            airport_lat = self.airportsPath[fieldlist]["LAT"]
                            airport_lon = self.airportsPath[fieldlist]["LON"]
                            sigmetlat, sigmetlon = u["lat"],u["lon"]

                            #Check to see if any point of the sigmet is within 50 nm of the airfield
                            if ((sigmetlat - .8333 < airport_lat < sigmetlat + .8333) and (sigmetlon - .8333 < airport_lon < sigmetlon + .8333)):
                                isEligible = True
                            #If there isn't a point within 50 miles,  check to see if the airport is inside some huge box
                            elif ((min(siglat) < airport_lat < max(siglat)) and (min(siglon) < airport_lon < max(siglon))):
                                isEligible = True
                        except:
                            return
            if isEligible:
                hazard = i["hazard"]
                type = i["airSigmetType"]
                rawsigmet = i["rawAirSigmet"].splitlines()
                self.sigmet_list.append(i["airSigmetId"])
                if type == "SIGMET":
                    self.printer.print_gi_messages(f'{rawsigmet[0]}{rawsigmet[1]}{rawsigmet[2]}{rawsigmet[3]}... {rawsigmet[4]}... {rawsigmet[5]}... {rawsigmet[6]}{rawsigmet[7]}')
                #    self.printer.print_gi_messages(f'{rawsigmet[2]} {rawsigmet[3]}... {rawsigmet[4]}... {rawsigmet[6]}{rawsigmet[7]}')
                elif type == "AIRMET":
                    gi_message = (f'{rawsigmet[0]}{rawsigmet[1]} {rawsigmet[2]} {rawsigmet[3]} {rawsigmet[4]} {rawsigmet[5]} {rawsigmet[6]}') 
                #    gi_message = (f'{rawsigmet[2]} {rawsigmet[3]} {rawsigmet[6]}')
                    self.printer.print_gi_messages(gi_message)
    
    def fetch_cwas(self, api, center):
        api = f'{self.cwasJSON}{(self.airportsPath[self.control_area["airports"][0]]["ARTCC"])}/cwas'
        r = requests.get(api)
        raw = r.json()
        # print(raw)
        for i in raw["features"]:
            id = i["properties"]["sequence"]
            advzy = i["properties"]
            if id not in self.cwa_list:
                cwsu = advzy['cwsu']
                hazard = advzy["text"]
                # print(f'GI G1 {cwsu} CWA {id} for {hazard}.')
                gi_message = f'***{cwsu} CWA {id} for {hazard}'
                self.printer.print_gi_messages(gi_message)
                self.cwa_list.append(id)

    def wxsync(self):
        #Sync up the time so that if theres a bunch of printers... they all print at the same time?
        timenow = tuple(time.gmtime())
        
        minutes = timenow[4]
        while (minutes > 5):
            minutes = minutes - 5
        
        delaytime = ((5 - minutes) * 60) + 60
        return delaytime