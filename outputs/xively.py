#!/usr/bin/env python

import output
import requests
import json

class Xively(output.Output):
    requiredData = ["APIKey", "FeedID"]
    optionalData = []
    def __init__(self, data):
        self.APIKey = data["APIKey"]
        self.FeedID = data["FeedID"]
    def outputData(self, dataPoints):
        arr = []
        try:
            for i in dataPoints:
                # handle GPS data
                if i["name"] == "Location":
                    arr.append({"location": {"disposition": i["disposition"], "exposure": i["exposure"], "domain": "physical", "ele": i["altitude"], "lat": i["latitude"], "lon": i["longitude"]}})
                else:
                    arr.append({"id": i["name"], "current_value": i["value"]})
            a = json.dumps({"version": "1.0.0", "datastreams": arr})
            z = requests.put("https://api.xively.com/v2/feeds/" + self.FeedID + ".json", headers = {"X-ApiKey":self.APIKey}, data = a)
            if z.text != "":
                print "Xively Error: " + z.text
                return False
            return True
        except Exception as e:
            raise e
