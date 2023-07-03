import requests
import time
import json
import math
from DataCollector import DataCollector
#If theres a SIGMET then default reason -> wx/tstorms>


#OK so this needs to do a couple of things
# Number onely, it needs to SCAN when airplanes come IN and LOG that time.
# TWOsely, it needs to SCAN when airplanes go OUT and log THAT time. Calculate the time between.
# We could have a discord bot that alerts us when delays reach 15 minutes & a "DROP" command for people who disconnect or whatevs. 
# Or it could "scan" to see if they're still connected and auto-drop that way.

# 3, when local scans flight strip, it needs to transmit that data (plus visual/not visual) to a80 AND check to see if theres a timer running for the aircraft. 
# if so, stop that timer and see what the delay is.

###

###IT JUST occured to me that this needs to NETWORK with other positions to get the in/out time lol oops

class Scanner:
    def __init__(self, control_area, sigmetJSON, printerpositions, airfields, data_collector: DataCollector) -> None:
        self.averageTaxiTime = 10
        self.reportInterval = 15
        self.data_collector = data_collector
        self.control_area = control_area
        self.controlType = control_area['type']
        self.sigmetJSON = sigmetJSON
        config = printerpositions
        self.averageTaxiTime = config['delayReporting']['averageTaxiTime']
        self.discord = config['delayReporting']['discordWebhook']
        self.airports = airfields        
        self.sigmets = []
        self.queue = {} #Format is callsign:time.time(). Example: queue = {"N69":time.time()}
        self.totalDelay = {} #Format is "callsign":{"totalDelay":0, "outTime":0}. "Example = totalDelay = {N70":{"totalDelay":0,"outTime":0}} 
        self.maxReportedDelay = 0

    def scan(self, callsign):
        position = self.controlType
        if position == "GC":
            self.startClock(callsign)
        elif position == "LC":
            self.sendDeparture(callsign)

    def startClock(self, callsign):
        if callsign not in self.queue:
            currentTime = time.time()
            self.queue[callsign] = currentTime
            print(self.queue)
    #    else: #This is for BUG TESTING PURPOSES Lol
    #        self.sendDeparture(callsign)

    def sendDeparture(self, callsign):
        print(self.queue)
        if callsign in self.queue:
            #Determine Delay
            startTime = self.queue[callsign]
            currentTime = time.time()
            totalDelay = (currentTime - startTime) / 60
            totalDelay = math.floor(totalDelay)
        #    self.totalDelay[callsign] = {"totalDelay":totalDelay,"outTime":currentTime}
        #    print(self.totalDelay[callsign])
            self.queue.pop(callsign)
        self.pushDeparture(callsign)
        print(self.queue)

    def purgeQueue(self):
        self.queue = {}
        self.totalDelay = {}
        self.maxReportedDelay = 0

    def opsNet(self):
        self.maxReportedDelay = 0
        while True:
            time.sleep(15)
            #Get the latest JSON File. We'll use this to see if a departure disconnected - if they did, we'll purge them from the list.
            acftList = self.data_collector.get_json()
            yourmom = set()
            for x in acftList['pilots']:
                yourmom.add(x['cid'])

            totalDelay = []

            #Ascertain current delays
            for aircraft in self.queue.copy():
                currentTime = time.time()
                aircraftDelay = (currentTime - self.queue[aircraft]) / 60
                aircraftDelay = math.floor(aircraftDelay)
                
                #Check to see if the aircraft is even still connected. If its not, purge the callsign.
                if int(aircraft) in yourmom:
                    totalDelay.append(aircraftDelay)
                else:
                    self.queue.pop(aircraft)
            
            for aircraft in self.totalDelay:
                totalDelay.append(self.totalDelay[aircraft]['totalDelay'])
                self.totalDelay.pop(aircraft)
            
            #Calculate the maximum delay
            maxDelay = 0
            try:
                maxDelay = max(totalDelay)
            except:
                continue

            #Correct for airport taxi times
            maxDelay = maxDelay - self.averageTaxiTime

            #If the max delay is... negative... let's correct for that lol
            if maxDelay < 0:
                maxDelay = 0

            #Now, let's see if its a reportable delay.
            if maxDelay % self.reportInterval == 0:
                if maxDelay > self.maxReportedDelay: #The delay hasn't been reported!
                    self.maxReportedDelay = maxDelay
                    cause = self.DelayOrigin()
                    self.reportDelay(self.maxReportedDelay,"+", cause)
                if maxDelay < self.maxReportedDelay: #The delays are going down!!!
                    self.maxReportedDelay = maxDelay
                    cause = self.DelayOrigin()
                    self.reportDelay(self.maxReportedDelay,"-", cause)
    #        print(maxDelay)

    def reportDelay(self, value, status, cause):
        #Come back to make "content" a cool lil Discord embed 
        if status == "+":
            rangeTime = f"{value} to {value + self.reportInterval} minutes"
            longStatus = "and INCREASING"
        elif status == "-":
            rangeTime = f"{value - self.reportInterval} to {value} minutes"
            longStatus = "and DECREASING"

        charge = cause.split(":")
        chargeCategory = {"WX":"Weather", "EQUIPMENT":"Equipment", "RWY":"Runway/Taxiway","VOL":"Volume","OTHER":"Other"}
        chargeClass = {"LOCIGS":"Low Ceilings","TSTORMS":"Thunderstorms","WIND":"Wind","LOVIS":"Low Visibility","FOG":"Fog","SNO":"Snow/Ice","TOR":"Tornado/Hurricane","BRAKING":"Poor/Nil Braking Action","RAIN":"Rain","RWY":"Runway","LTG":"Lightning Strike","FAA":"FAA (STARS/ERAM)","NOFAA":"Non-FAA","RWYCHG":"Runway Change - Operational Advantage","NOISE":"Noise Abatement","DISABLED AC":"Disabled Aircraft","COMPACT":"Compacted Demand","MULTI":"Multi-Taxi","VOL":"Volume","":"Airshow","EMER":"Aircraft Emergency","RDO":"Aircraft Radio","MIKE":"Aircraft Stuck Mike","BIRDS":"Bird Strike","FIRE":"Fire","FLC":"Flight Check","MIL":"Military Operations","PRM":"Precision Runway Monitor (PRM) non-equipage","LAHSO":"Aircraft/Pilot unable to perform land and hold short operations (LAHSO)","SEC":"Security","VIP":"VIP Movement","LUAW":"Line Up And Wait","OTHER":"Other"}

        aeroport = self.control_area['airports'][0]
        content = {"content":f"""D/D from {aeroport}, {status}{value} due to {cause}.
        There are departure delays from **{self.airports['airfields'][aeroport]['NAME']}** of {rangeTime} ({longStatus}) due to {chargeCategory[charge[0]]}:{chargeClass[charge[1]]}."""}
       # content = {"content":"help","embeds":[{"title":"ATL Departure Delays"},"footer":{}]}
        #status = up or down
        #value = numbers
        requests.post(self.discord, content)

    def DelayOrigin(self):
        #Find the METAR for the airport
        metarJSON = requests.get(f'https://api.weather.gov/stations/{(self.control_area["airports"][0])}/observations/latest').json()
        rawMetar = metarJSON['properties']['rawMessage']
        textDescription = metarJSON['properties']['textDescription']
        
        wx = {"fog_mist":"LOVIS", "dust_storm":"LOVIS", "dust":"LOVIS", "drizzle":"RAIN", "funnel_cloud":"TOR", "fog":"FOG", "smoke":"LOVIS", "hail":"TSTORMS", "snow_pellets":"SNO", "haze":"LOVIS", "ice_crystals":"SNO", "ice_pellets":"SNO", "dust_whirls":"TOR", "spray":"RAIN", "rain":"RAIN", "sand":"LOVIS", "snow_grains":"LOVIS", "snow":"SNO", "squalls":"TSTORMS", "sand_storm":"TSTORMS", "thunderstorms":"TSTORMS", "unknown":"OTHER", "volcanic_ash":"LOVIS"}
        wxCharge = False

        #Check if its one of the weather conditions listed in "wx".
        for condition in wx:
            if condition in textDescription:
                wxCharge = condition
                print(condition)
                continue

        #Assign a cause.
        if wxCharge is not False:
            return f"WX:{wxCharge}"
        elif self.sigmets is not None:
            return "WX:TSTORMS"
        else:
            return "VOL:Volume"

    def pushDeparture(self,callsign):
        visualFlag = False
        print(f'PUSHING {callsign} TO DEPARTURE RADAR. VISUAL SEPARATION: {visualFlag}.')
