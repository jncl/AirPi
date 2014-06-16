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

# chr(165) could be degree symbol
# chr(223) could be degree symbol

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
        self.blankline = " " * self.cols
        self.lcd = lcddriver.lcd()
        clearDisplay()

    def outputData(self, dataPoints):
        line = 1
        self.lcd.clear(bl=1)
        for i in dataPoints:
            self.lcd.display_string(self.blankline, line)
            # handle GPS data
            if i["type"] == "Location":
                disp_str = "GPS: {0} {1} {2}".format(i["lat"], i["lon"], i["ele"])
            else:
                disp_str = "{0}: {1:.2f} {2}".format(abbr[i["type"]], i["value"], i["symbol"])
            self.log.debug(disp_str)
            self.lcd.display_string(disp_str, line)
            sleep(0.4)
            line += 1
            if line > self.rows:
                line = 1

    def clearDisplay()
        self.lcd.clear(bl=0)
