from DataCollector import DataCollector
import time
import requests
import re

__author__ = "Simon Heck"

class JSONRefreshTimer:
    def __init__(self, data_collector:DataCollector) -> None:
        self.data_collector = data_collector

    def start_refreshing(self, delay:int = 15):
        while(True):
            time.sleep(delay)
            self.data_collector.check_for_updates()

    def calculateDelay(self, json_url):
        print("Syncing data... please wait!")
        start_time = (requests.get(json_url).json())["general"]["update_timestamp"]
        jsonSeconds = re.findall(":..", start_time) #find seconds
        jsonSeconds = int(re.sub(":","",jsonSeconds[1])) #clean up seconds so we can make it an integer
        #print(start_time) # For debugging / Testing purposes... gotta know what we're starting with
        #print(time.ctime()) # Know where we're at to see if the delay is... right

        #Calculate when the next refresh SHOULD happen
        timeToWait = 0
        nextRefresh = jsonSeconds + 15

        #IDK how to do math so I did this instead
        if nextRefresh > 45:
            nextRefresh = nextRefresh - 45

        timeNow = time.gmtime().tm_sec
        if timeNow > 45:
            timeNow = timeNow - 45
        
        #Correct for weird stuff?
        timeToWait = nextRefresh - timeNow
        while timeToWait < 0:
            timeToWait = timeToWait + 15
        
        while timeToWait > 15:
            timeToWait = timeToWait - 15

        timeToWait = timeToWait + 1 # Add 1 second as a buffer incase of drift or whatever
        print("Estimated wait time is " + str(timeToWait)+ " seconds.")
        time.sleep(timeToWait)
        print("Delay implemeted and data synced. Unlocking program. Happy stripping!")
        return