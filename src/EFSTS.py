import requests
import time
#If theres a SIGMET then default reason -> wx/tstorms>


#OK so this needs to do a couple of things
# Number onely, it needs to SCAN when airplanes come IN and LOG that time.
# TWOsely, it needs to SCAN when airplanes go OUT and log THAT time. Calculate the time between.
# We could have a discord bot that alerts us when delays reach 15 minutes & a "DROP" command for people who disconnect or whatevs. 
# Or it could "scan" to see if they're still connected and auto-drop that way.

# 3, when local scans flight strip, it needs to transmit that data (plus visual/not visual) to a80 AND check to see if theres a timer running for the aircraft. 
# if so, stop that timer and see what the delay is.


###



#Gonna have this pull from positions.json soon enough, but for now...:
discord = "https://discord.com/api/webhooks/1124601273078005830/Nf2AARyX5Gif_gszLx4qYfp6Jf4_2p_4OfBhExtz-yMES84F3SQMscfFq5UTxkyunIEf"

content = {"content":"""D/D from ATL, 15+ due to WX:TSTORMS
There are departure delays from **ATLANTA** of 15 to 30 minutes (and increasing) due to WEATHER:THUNDERSTORMS."""}

#Come back to make "content" a cool lil Discord embed 
#content = {"content":"help","embeds":[{"title":"ATL Departure Delays"},"footer":{}]}

requests.post(discord, content)


class Scanner:
    def __init__(self, control_area, sigmetJSON):
        self.control_area = control_area
        self.sigmetJSON = sigmetJSON
        sigmets = []
        self.times = {}
        totalDelay = 0

    def startClock(self, callsign):
        if callsign not in self.times:
            self.times.append(callsign,time.gmtime)
    
    def sendDeparture(self, callsign):
        if callsign in self.times:
            totalTime = self.times[callsign[1]]
            self.times.popitem(callsign)

    def opsNet(self):
        while True:
            time.sleep(1)
            for aircraft in self.times:
                print(aircraft)
