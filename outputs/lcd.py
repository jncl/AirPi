import output
import os
import lcddriver

# add logging support
import logging
mod_log = logging.getLogger('airpi.lcd')

class Database(output.Output):
    requiredData = []
    optionalData = []
    lcd = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.lcd')
        self.lcd = lcddriver.lcd()
        self.lcd.clear(bl=0)

    def outputData(self, dataPoints):
        for i in dataPoints:
            # handle GPS data
            if i["type"] == "Location":
                self.lcd.display_string("Lat: {0}, Lon: {1}, Elev: {2}".format(i["lat"], i["lon"], i["ele"]))
            else:
                self.lcd.display_string("{0}: {1}{2}".format(i["type"], i["value"], i["symbol"]))
