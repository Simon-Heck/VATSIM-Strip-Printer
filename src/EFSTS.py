import requests
import time
import json
import math
from DataCollector import DataCollector
#If theres a SIGMET then default reason -> wx/tstorms>


#OK so this needs to do a couple of things
# Number onely, it needs to SCAN when airplanes come IN and LOG that time. [Done]
# TWOsely, it needs to SCAN when airplanes go OUT and log THAT time. Calculate the time between. [Done]
# We could have a discord bot that alerts us when delays reach 15 minutes & a "DROP" command for people who disconnect or whatevs.  [Done]
# Or it could "scan" to see if they're still connected and auto-drop that way. [Also done]

# 3, when local scans flight strip, it needs to transmit that data (plus visual/not visual) to a80 AND check to see if theres a timer running for the aircraft.  [Half done]
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
            self.start_clock(callsign)
        elif position == "LC":
            visualFlag = False
            if callsign[0] == "v" and callsign[1:].isnumeric():
                visualFlag = True
            self.send_departure(callsign, visualFlag)

    def start_clock(self, callsign):
        if callsign.isnumeric() == False:
            #We only want numbers being tracked.
            return
        if callsign not in self.queue:
            currentTime = time.time()
            self.queue[callsign] = currentTime
        else: #This is for bug testing purposes.
            self.send_departure(callsign)

    def send_departure(self, callsign, visualFlag=""):
        if visualFlag is None:
            visualFlag = False
        if callsign in self.queue:
            #Determine Delay
            startTime = self.queue[callsign]
            currentTime = time.time()
            totalDelay = (currentTime - startTime) / 60
            totalDelay = math.floor(totalDelay)
            self.totalDelay[callsign] = totalDelay
            print(self.totalDelay[callsign])
            self.queue.pop(callsign)
        self.push_departure(callsign, visualFlag)

    def purgeQueue(self):
        self.queue = {}
        self.totalDelay = {}
        self.maxReportedDelay = 0
        print("Queue purged. Current delays set to 0.")

    def listTimes(self):
        self.times = {}
        for x in self.queue.copy():
            currentTime = time.time()
            aircraftDelay = (currentTime - self.queue[x]) / 60
            aircraftDelay = math.floor(aircraftDelay)
            self.times[x] = aircraftDelay
        print(f"Normal airport taxi time: {self.averageTaxiTime} minutes. Current taxi times:{self.times}.")

    def dropTime(self,callsign):
        try:
            self.queue.pop(callsign)
            print(f"Removed {callsign} from delay tracking.")
        except:
            print(f"Unable to find {callsign}. Sorry!")


    def opsNet(self):
        self.maxReportedDelay = 0
        while True:
            time.sleep(15)
            #Get the latest JSON File. We'll use this to see if a departure disconnected - if they did, we'll purge them from the list.
            acftList = self.data_collector.get_json()
            connectedAircraft = set()
            for x in acftList['pilots']:
                connectedAircraft.add(x['cid'])

            totalDelay = []

            #Ascertain current delays
            for aircraft in self.queue.copy():
                currentTime = time.time()
                aircraftDelay = (currentTime - self.queue[aircraft]) / 60
                aircraftDelay = math.floor(aircraftDelay)
                
                #Check to see if the aircraft is even still connected. If its not, purge the callsign.
                if int(aircraft) in connectedAircraft:
                    totalDelay.append(aircraftDelay)
                else:
                    self.queue.pop(aircraft)
            
            for aircraft in self.totalDelay.copy():
                totalDelay.append(self.totalDelay[aircraft])
                self.totalDelay.pop(aircraft)
            
            #Calculate the maximum delay
            maxDelay = 0
            try:
                maxDelay = max(totalDelay)
            except:
                continue

            #Correct for airport taxi times
            maxDelay = maxDelay - self.averageTaxiTime

            #If the max delay is... negative... let's correct for that.
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
        chargeClass = {"LOCIGS":"Low Ceilings","TSTORMS":"Thunderstorms","TSTORMS":"Thunderstorms","WIND":"Wind","LOVIS":"Low Visibility","FOG":"Fog","SNO":"Snow/Ice","TOR":"Tornado/Hurricane","BRAKING":"Poor/Nil Braking Action","RAIN":"Rain","RWY":"Runway","LTG":"Lightning Strike","FAA":"FAA (STARS/ERAM)","NOFAA":"Non-FAA","RWYCHG":"Runway Change - Operational Advantage","NOISE":"Noise Abatement","DISABLED AC":"Disabled Aircraft","COMPACT":"Compacted Demand","MULTI":"Multi-Taxi","VOL":"Volume","":"Airshow","EMER":"Aircraft Emergency","RDO":"Aircraft Radio","MIKE":"Aircraft Stuck Mike","BIRDS":"Bird Strike","FIRE":"Fire","FLC":"Flight Check","MIL":"Military Operations","PRM":"Precision Runway Monitor (PRM) non-equipage","LAHSO":"Aircraft/Pilot unable to perform land and hold short operations (LAHSO)","SEC":"Security","VIP":"VIP Movement","LUAW":"Line Up And Wait","OTHER":"Other"}

        aeroport = self.control_area['airports'][0]
        logDay = '{:0>2}'.format(time.gmtime().tm_mday)
        logHour = '{:0>2}'.format(time.gmtime().tm_hour)
        logMin = '{:0>2}'.format(time.gmtime().tm_min)
        logTime = f'{logDay}/{logHour}{logMin}'
        content = {"content":f"""{logTime}   D/D from {aeroport}, {status}{value} due to {cause}.
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
        textDescription = textDescription.lower()
        
        wx = {"fog_mist":"LOVIS", "dust_storm":"LOVIS", "dust":"LOVIS", "drizzle":"RAIN", "funnel_cloud":"TOR", "fog":"FOG", "smoke":"LOVIS", "hail":"TSTORMS", "snow_pellets":"SNO", "haze":"LOVIS", "ice_crystals":"SNO", "ice_pellets":"SNO", "dust_whirls":"TOR", "spray":"RAIN", "rain":"RAIN", "sand":"LOVIS", "snow_grains":"LOVIS", "snow":"SNO", "squalls":"TSTORMS", "sand_storm":"TSTORMS", "thunderstorms":"TSTORMS", "unknown":"OTHER", "volcanic_ash":"LOVIS"}
        wxCharge = False
        volumeCharge = False

        #Check if its one of the weather conditions listed in "wx".
        for condition in wx:
            if condition in textDescription:
                wxCharge = wx[condition]
                continue
        
        if len(self.queue) >= self.reportInterval + self.averageTaxiTime:
            volumeCharge = True

        #Assign a cause.
        if wxCharge is not False:
            return f"WX:{wxCharge}"
        elif len(self.sigmets) > 0:
            return "WX:TSTORMS"
        elif volumeCharge:
            return "VOL:VOL"
        else:
            return "OTHER:OTHER"

    def push_departure(self, callsign, visualFlag):
        print(f'PUSHING {callsign} TO DEPARTURE RADAR. VISUAL SEPARATION: {visualFlag}.')