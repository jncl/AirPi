# -*- coding: utf-8 -*-
import output
import os
import lcddriver
from time import sleep

try:
    unichr = unichr
except NameError:  # Python 3
    unichr = chr

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
ds = unichr(223)

# add logging support
import logging
mod_log = logging.getLogger('airpi.lcdpanel')

class LCDpanel(output.Output):
    requiredData = ["cols", "rows"]
    optionalData = []
    lcd = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.lcdpanel')
        self.cols = int(data["cols"])
        self.rows = int(data["rows"])
        self.blankline = " " * self.cols
        try:
            self.lcd = lcddriver.lcd()
            self.lcd.display_string("  Airpi LCD panel   ", 2)
            self.lcd.display_string(" Init was a Success ", 3)
        except Exception as e:
            self.log.error("Error initialising LCDpanel: {0}".format(e))
            raise
        else:
            self.log.debug("Initialised successfully")

    def outputData(self, dataPoints):
        line = 1
        try:
            self.lcd.clear(bl=1)
            for i in dataPoints:
                print(i)
                self.log.debug(i)
                self.lcd.display_string(self.blankline, line)
                disp_str = ""
                # handle GPS data when available
                if i["type"] == "Location":
                    if i["lat"] > 0.0:
                        disp_str = "GPS: {0:.3f}{1} N {2:.3f}{3} W {4}".format(i["lat"], ds, i["lon"], ds, i["ele"])
                    else:
                        continue
                else:
                    disp_str = "{0}: {1:.2f} {2}".format(abbr[i["type"]], i["value"], i["symbol"])
                # display data on LCD panel
                self.lcd.display_string(disp_str, line)
                self.log.debug("Display string: {0}, {1}".format(disp_str, line))
                sleep(0.4)
                line += 1
                if line > self.rows:
                    line = 1
        except Exception as e:
            self.log.error("Error displaying string on LCD: {0}".format(e))
            raise
        else:
            return True

    def clearDisplay(self, bl=0):
        self.log.info("Clearing LCD panel & turning off backlight")
        try:
            self.lcd.clear(bl=bl)
        except Exception as e:
            self.log.error("Error clearing LCD panel: {0}".format(e))
            raise
