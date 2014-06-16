import output
import os
import lcddriver
from time import sleep

abbr = {
    "Temperature" : "Temp",
    "Pressure" : "P",
    "Relative_Humidity" : "RH",
    "Light_Level" : "LL",
    "Light_Level_Lux" : "LLl",
    "Nitrogen_Dioxide" : "NO2",
    "Carbon_Monoxide" : "CO",
    "Volume" : "Vol"
}


# add logging support
import logging
mod_log = logging.getLogger('airpi.lcd')

class Database(output.Output):
    requiredData = ["cols", "rows"]
    optionalData = []
    lcd = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.lcd')
        self.cols = int(data["cols"])
        self.rows = int(data["rows"])
        self.lcd = lcddriver.lcd()
        self.lcd.clear(bl=0)

    def outputData(self, dataPoints):
        line = 1
        self.lcd.clear(bl=1)
        for i in dataPoints:
            self.log.debug("type: {0}, value: {1:.2f}, symbol: {2}".format(i["type"][:1], i["value"], i["symbol"]))
            # handle GPS data
            if i["type"] == "Location":
                self.lcd.display_string("GPS: {0} {1} {2}".format(i["lat"], i["lon"], i["ele"]), line)
            else:
                self.lcd.display_string("{0}: {1:.2f} {2}".format(abbr[i["type"]], i["value"], i["symbol"]), line)
            sleep(2)
            line += 1
            if line > self.rows:
                line = 1
