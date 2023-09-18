import time
import json
from DataCollector import DataCollector

#COMMAND STRUCTURE IS ALL or DEPARTURE NORTH/CENTER/SOUTH

class AirspaceManagement:
    def __init__(self, control_area, data_collector: DataCollector) -> None:
        #Variables here...
        currentSplit = {
            "N":["NOONE","NOTWO","PENCL","VARNM","PADGT","SMKEY","WEONE","WETWO","POUNC","KAJIN","NASSA","CUTTN"],
            "C":["EAONE","EATWO","PLMMR","JACCC","PHIIL","GAIRY","SOONE","SOTWO","VRSTY","SMLTZ","BANNG","HAALO"],
            "S":[],
        }

        normalSplit = {
            "NOONE":"N", "NOTWO":"N", "PENCL":"N", "VARNM":"N", "PADGT":"N", "SMKEY":"N",
            "WEONE":"N", "WETWO":"N", "POUNC":"N", "KAJIN":"N", "NASSA":"N", "CUTTN":"N",
            "EAONE":"C", "EATWO":"C", "PLMMR":"C", "JACCC":"C", "PHIIL":"C", "GAIRY":"C",
            "SOONE":"C", "SOTWO":"C", "VRSTY":"C", "SMLTZ":"C", "BANNG":"C", "HAALO":"C"
            }

        gateFixes = {
            "EAONE":["EAONE", "PLMMR", "JACCC"],
            "EATWO":["EATWO", "PHIIL", "GAIRY"],
            "SOONE":["SOONE", "VRSTY", "SMLTZ"],
            "SOTWO":["SOTWO", "BANNG", "HAALO"],
            "WEONE":["WEONE", "POUNC", "KAJIN"],
            "WETWO":["WETWO", "NASSA", "CUTTN"],
            "NOONE":["NOONE", "PENCL", "VARNM"],
            "NOTWO":["NOTWO", "PADGT", "SMKEY"]
        }

        depCodes = {
            "E1":"EAONE",
            "E3":"PLMMR",
            "E5":"JACCC",
            "E2":"EATWO",
            "E4":"PHIIL",
            "E6":"GAIRY",
            "W1":"WEONE",
            "W3":"POUNC",
            "W5":"KAJIN",
            "W2":"WETWO",
            "W4":"NASSA",
            "W6":"CUTTN",
            "N1":"NOONE",
            "N3":"PENCL",
            "N5":"VARNM",
            "N2":"NOTWO",
            "N4":"PADGT",
            "N6":"SMKEY",
            "S1":"SOONE",
            "S3":"SMLTZ",
            "S5":"VRSTY",
            "S2":"SOTWO",
            "S4":"BANNG",
            "S6":"HAALO"
        }

        proposals = {
            "EAONE":0,
            "PLMMR":0,
            "JACCC":0,
            "EATWO":0,
            "PHIIL":0,
            "GAIRY":0,
            "WEONE":0,
            "POUNC":0,
            "KAJIN":0,
            "WETWO":0,
            "NASSA":0,
            "CUTTN":0,
            "NOONE":0,
            "PENCL":0,
            "VARNM":0,
            "NOTWO":0,
            "PADGT":0,
            "SMKEY":0,
            "SOONE":0,
            "SMLTZ":0,
            "VRSTY":0,
            "SOTWO":0,
            "BANNG":0,
            "HAALO":0
        }

        self.currentSplit = currentSplit
        self.gateFixes = gateFixes
        self.normalSplit = normalSplit
        self.controlArea = control_area
        self.FTD = False
        self.datacollector = data_collector
        self.proposals = proposals
        self.depCodes = depCodes
    
    def getSplit(self) -> str:
        time.sleep(.5)
        while(True):
            splitPosition = input("Enter ARMT command: ")
            
            splitPosition = self.formatCommand(splitPosition)

            if splitPosition[:3] == "ftd":
                #try:
                #    self.FTD = bool(int(input("Do you want to activate the 3rd runway? Reply '1' for yes or '0' for no.")))
                #    if self.FTD == False:
                #        self.amendSplit("normal")
                #except:
                #    continue
                if self.FTD:
                    self.FTD = False
                    print("Third runway OFF")
                else:
                    self.FTD = True
                    print("Third runway ON")

            if splitPosition[:3] == "all":
                self.amendSplit(splitPosition)

            if splitPosition.upper()[:5] in self.normalSplit:
                self.amendSplit(splitPosition)
            elif splitPosition[:6] == "normal":
                self.amendSplit("normal")
            elif splitPosition[:13] == "countproposal":
                self.countProposals()
            elif splitPosition in ["worstqueue","queuecount","q", "queue"]:
                self.worstQueue()

    def amendSplit(self, input):
        input = input.replace(" ","")
        engToCode1 = {"north":"N","center":"C","south":"S"}
        try:
            if input[:3] == "all":
                newCode = engToCode1[input[3:]]
                print("change the split!!")
                self.currentSplit = {"N":[],"C":[],"S":[]}
                for i in self.normalSplit:
                    self.currentSplit[newCode].append(i)
                print(self.currentSplit)
            elif input == "normal":
                print("normal split, coming up!")
                self.currentSplit = {"N":[],"C":[],"S":[]}
                for i in self.normalSplit:
                    self.currentSplit[self.normalSplit[i]].append(i)
                print(self.currentSplit)
            else:
                newCode = engToCode1[input[5:]]
                input = input.upper()
                print(f"change the split!! moving {input[:5]} to the {newCode}")
                if input[:5] in self.gateFixes:
                    for x in self.gateFixes[input[:5]]:
                        for i in self.currentSplit:
                            if x in self.currentSplit[i]:
                                self.currentSplit[i].remove(x)
                        self.currentSplit[newCode].append(x)
                else:
                    for i in self.currentSplit:
                        if input[:5] in self.currentSplit[i]:
                            self.currentSplit[i].remove(input[:5])
                    self.currentSplit[newCode].append(input[:5])
                print(self.currentSplit)
            
        except:
            print("huh?")
    

    
    def countProposals(self):
        proposals = self.countProposalsMath()
        print(proposals)


    def worstQueue(self):
        queues = self.countProposalsMath()
        queueCount = {"N":0,"C":0,"S":0}        
        for i in queues:
            for u in self.currentSplit:
                if i in self.currentSplit[u]:
                    queueCount[u] = queueCount[u] + queues[i]
        print(queueCount)

    def countProposalsMath(self):
        aircraft = {}
        proposedDeps = {}

        for i in self.proposals:
            self.proposals[i] = 0
        
        json_File = self.datacollector.get_json()
        json_File = json_File['pilots']
        for i in range(len(json_File)):
            # pilot at index i information
            current_pilot = json_File[i]
            ### ---- Finding out if an aircraft is eligable to be reported.
            try:
                lat_long_tuple = (current_pilot['latitude'], current_pilot['longitude'])
                pilot_departure_airport = current_pilot['flight_plan']['departure']
                if pilot_departure_airport == "KATL" and self.datacollector.in_geographical_region_wip(self.controlArea, pilot_departure_airport, lat_long_tuple):
                    aircraft[current_pilot['callsign']] = current_pilot['flight_plan']['route']
            except:
                continue

        
        for i in aircraft:
            for types in self.proposals:
                if types in aircraft[i]:
                    self.proposals[types] = self.proposals[types] + 1
        for i in self.proposals:
            if self.proposals[i] > 0:
                proposedDeps[i] = self.proposals[i]
        return proposedDeps

                    
    def formatCommand(self, splitPosition):
        splitPosition = splitPosition.lower()
        try:
            if splitPosition[-1] in ["n","c","s"]:
                elongator = {"n":"north","c":"center","s":"south"}
                splitPosition = f'{splitPosition[:-1]}{elongator[splitPosition[-1]]}'

            if self.FTD is False:
                splitPosition = splitPosition.replace("south","center")

            splitPosition = splitPosition.replace(" ","")
            if splitPosition[1].isnumeric():
                splitPosition = splitPosition.replace(splitPosition[:2],self.depCodes[splitPosition.upper()[:2]]).lower()
        except:
            print("damn")
        return splitPosition
            