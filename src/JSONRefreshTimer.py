from DataCollector import DataCollector
import time
import requests
import re

__author__ = "Zack B"

class JSONRefreshTimer:
    def __init__(self, data_collector:DataCollector, json_url) -> None:
        self.data_collector = data_collector
        self.json_url = json_url

    def start_refreshing(self, delay:int = 15):
        self.calculateDelay(self.json_url)
        while(True):
            time.sleep(delay)
            self.data_collector.check_for_updates()

    def calculateDelay(self, json_url):
        print("Syncing data... please wait!")
        start_time = (requests.get(json_url).json())["general"]["update_timestamp"]
        jsonSeconds = re.findall(":..", start_time) #find seconds
        jsonSeconds = int(re.sub(":","",jsonSeconds[1])) #clean up seconds so we can make it an integer

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
        if timeToWait == 16:
            timeToWait = 0 #Literally means it doesn't need to refresh lol
            print("Jackpot!")
        print("Estimated wait time until next refresh is " + str(timeToWait)+ " seconds. Unlocking program. Happy stripping!")
        time.sleep(timeToWait)
        return