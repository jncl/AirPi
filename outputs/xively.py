import output
import requests
import json

# add logging support
import logging
log = logging.getLogger('AirPi')

class Xively(output.Output):
    requiredData = ["APIKey", "FeedID"]
    optionalData = ["gpsLocn"]

    def __init__(self, data):
        self.URL = "https://api.xively.com/v2/feeds/" + data["FeedID"] + ".json"
        self.headers = ({"X-ApiKey": data["APIKey"]})
        self.gpsLocn = None
        if "gpsLocn" in data:
            self.gpsLocn = data["gpsLocn"]

    def outputData(self, dataPoints):
        arr = []
        a = l = z = None

        try:
            for i in dataPoints:
                # handle GPS data
                if i["name"] == "Location":
                    l = ({"disposition": i["disposition"], "name": i["location"], "exposure": i["exposure"], "domain": "physical", "ele": i["altitude"], "lat": i["latitude"], "lon": i["longitude"]})
                else:
                    arr.append({"id": i["name"], "current_value": i["value"]})

            a = json.dumps({"version": "1.0.0", "datastreams": arr, "location": l})
            log.debug("Xively output: [{0}]".format(a,))

            # add a timeout for Mobile location
            if self.gpsLocn == "Mobile":
                z = requests.put(self.URL, headers = self.headers, data = a, timeout = 5.0)
            else:
                z = requests.put(self.URL, headers = self.headers, data = a)

            if z.text != "":
                log.error("Xively Error: {0}".format(z.text))
                return False
            return True
        except Exception as e:
            log.exception("Xively Exception: {0}".format(e))
            raise e
