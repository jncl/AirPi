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

class LCD(output.Output):
    requiredData = ["cols", "rows"]
    optionalData = []
    lcd = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.lcd')
        self.cols = int(data["cols"])
        self.rows = int(data["rows"])
        self.blankline = " " * self.cols
        self.lcd = lcddriver.lcd()
        self.lcd.clear(bl=0)

    def outputData(self, dataPoints):
        line = 1
        self.lcd.clear(bl=1)
        for i in dataPoints:
            print(i)
            self.log.debug(i)
            self.lcd.display_string(self.blankline, line)
            disp_str = ""
            # handle GPS data when available
            if i["type"] == "Location":
                if i["lat"] > 0.0:
                    disp_str = "GPS: {0:.2f} {1:.2f} {2}".format(i["lat"], i["lon"], i["ele"])
                else:
                    continue
            else:
                disp_str = "{0}: {1:.2f} {2}".format(abbr[i["type"]], i["value"], i["symbol"])
            try:
                self.log.debug(disp_str, line)
                self.lcd.display_string(disp_str, line)
                sleep(0.4)
                line += 1
                if line > self.rows:
                    line = 1
            except:
                raise

        return True

    def clearDisplay(self, bl=0):
        self.lcd.clear(bl=bl)
