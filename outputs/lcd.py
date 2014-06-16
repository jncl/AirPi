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
            self.log.debug("type: {0}, value: {1:.2f}, symbol: {2}".format(i["type"][:1], i["value"], i["symbol"]))
            self.log.debug("#1 line: {0}, rows: {1}".format(line, self.rows))
            # handle GPS data
            if i["type"] == "Location":
                self.lcd.display_string("GPS: {0} {1} {2}".format(i["lat"], i["lon"], i["ele"]), line)
            else:
                self.lcd.display_string("{0}: {1:.2f} {2}".format(i["type"][:1], i["value"], i["symbol"]), line)
            line += 1
            self.log.debug("#2 line: {0}".format(line))
            if line > self.rows:
                line = 1
                self.log.debug("#3 line: {0}".format(line))
