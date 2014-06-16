import output
import os
import lcddriver

# add logging support
import logging
mod_log = logging.getLogger('airpi.lcd')

class Database(output.Output):
    requiredData = ["cols", "rows"]
    optionalData = []
    lcd = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.lcd')
        self.cols = data["cols"]
        self.rows = data["rows"]
        self.lcd = lcddriver.lcd()
        self.lcd.clear(bl=0)

    def outputData(self, dataPoints):
        line = 1
        for i in dataPoints:
            # handle GPS data
            if i["type"] == "Location":
                self.lcd.display_string("Lat: {0}, Lon: {1}, Elev: {2}".format(i["lat"], i["lon"], i["ele"]), line)
            else:
                self.lcd.display_string("{0}: {1} {2}".format(i["type"][:1], i["value"][:8], i["symbol"]), line)
            line += 1
            if line > self.rows:
                line = 1
