import output
import lcddriver
from LcdScroller import LcdScroller
from time import sleep

try:
    unichr = unichr
except NameError:  # Python 3
    unichr = chr

# chr(223) is the degree symbol on LCD panel
ds = unichr(223)

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
mod_log = logging.getLogger('airpi.lcdpanel')

class LCDpanel(output.Output):
    requiredData = ["cols", "rows", "delay"]
    optionalData = []
    lcd = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.lcdpanel')
        self.cols = int(data["cols"])
        self.rows = int(data["rows"])
        self.delay = float(data["delay"])
        self.sl = [0, 1 ,1 ,1] # first line is static others scroll
        try:
            self.lcd = lcddriver.lcd()
            self.lcd.display_string("  Airpi LCD panel   ", 2)
            self.lcd.display_string(" Init was a Success ", 3)
            # setup LcdScroller thread object
            data = (u" Airpi Sensor Info. ", u"Temp: Unknown, P: Unknown, RH: Unknown ", u"LL: Unknown, LLl: Unknown, Vol: Unknown ", u"NO2: Unknown, CO: Unknown ")
            self.scroller = LcdScroller(self.lcd, self.rows, self.cols, self.delay, self.sl, data)
            self.scroller.start()
        except Exception as e:
            self.log.error("Error initialising LCDpanel: {0}".format(e))
            raise
        else:
            self.log.debug("Initialised successfully")

    def outputData(self, dataPoints):
        try:
            line1_str = line2_str = line3_str = line4_str = ""
            bl = 0
            for i in dataPoints:
                self.log.debug(i)
                disp_str = ""
                # handle GPS data when available
                if i["type"] == "Location":
                    # make line 1 scroll
                    self.sl[0] = 1
                    disp_str = u"DT: Unknown; Posn: Unknown; Alt: Unknown; "
                    if i["utc"] != None:
                        if i["lat"] > float(0.0):
                            disp_str = u"DT: {0} {1}; Posn: {2:.4f}{3},{4:.4f}{5}; Alt: {6} m; ".format(i["utc"][:10], i["utc"][11:19], i["lat"], ds, i["lon"], ds, i["ele"])
                elif i["type"] == "Temperature":
                    disp_str = u"{0}: {1:.1f}{2} {3}; ".format(abbr[i["type"]], i["value"], ds, i["symbol"])
                else:
                    disp_str = u"{0}: {1:.2f} {2}; ".format(abbr[i["type"]], i["value"], i["symbol"])

                # add to correct line string
                if i["type"] == "Location":
                    line1_str += disp_str
                elif i["type"] == "Temperature":
                    line2_str += disp_str
                elif i["type"] == "Pressure":
                    line2_str += disp_str
                elif i["type"] == "Relative_Humidity":
                    line2_str += disp_str
                elif i["type"] == "Light_Level":
                    line3_str += disp_str
                    if i["value"] < float(10.0):
                        # enable backlight at low light levels
                        bl = 1
                elif i["type"] == "Light_Level_Lux":
                    line3_str += disp_str
                elif i["type"] == "Volume":
                    line3_str += disp_str
                else:
                    line4_str += disp_str
            # update LcdScroller thread data
            self.scroller.updData((line1_str, line2_str, line3_str, line4_str), self.sl, bl)

        except Exception as e:
            self.log.error("Error displaying string on LCD: {0}".format(e))
            raise
        else:
            return True

    def clearLCD(self):
        print("Stopping LcdScroller thread")
        self.log.info("Stopping LcdScroller thread {0}".format(self.scroller.isAlive()))
        if self.scroller.isAlive():
            self.scroller.stopScroller()
            self.scroller.join()

        print("Clearing LCD panel & turning off backlight")
        self.log.info("Clearing LCD panel & turning off backlight")
        try:
            self.lcd.clear(bl=0)
        except Exception as e:
            self.log.error("Error clearing LCD panel: {0}".format(e))
            raise
