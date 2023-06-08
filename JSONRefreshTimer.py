import DataCollector
import time

__author__ = "Simon Heck"

class JSONRefreshTimer:
    def __init__(self, data_collector:DataCollector) -> None:
        self.data_collector = data_collector

    def start_refreshing(self, delay:int = 10):
        while(True):            
            time.sleep(delay)
            self.data_collector.update_proposed_departures()
