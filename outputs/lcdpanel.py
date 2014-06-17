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
            # setup LcdScroller thread objects
            data = (u"GPS: Unknown Unknown Unknown ", u"Temp: Unknown, P: Unknown, RH: Unknown ", u"LL: Unknown, LLl: Unknown, Vol: Unknown ", u"NO2: Unknown, CO: Unknown ")
            self.scroller = LcdScroller(self.lcd, self.rows, self.cols, data)
            # self.line1 = LcdScroller(self.lcd, 1, u"GPS: Unknown Unknown Unknown ")
            # self.line2 = LcdScroller(self.lcd, 2, u"Temp: Unknown, P: Unknown, RH: Unknown ")
            # self.line3 = LcdScroller(self.lcd, 3, u"LL: Unknown, LLl: Unknown, Vol: Unknown ")
            # self.line4 = LcdScroller(self.lcd, 4, u"NO2: Unknown, CO: Unknown ")
            self.scroller.start()
            # self.line2.start()
            # self.line3.start()
            # self.line4.start()
            # self.lcd.display_string("  Airpi LCD panel   ", 2)
            # self.lcd.display_string(" Init was a Success ", 3)
        except Exception as e:
            self.log.error("Error initialising LCDpanel: {0}".format(e))
            raise
        else:
            self.log.debug("Initialised successfully")

    def outputData(self, dataPoints):
        # line = 1
        try:
            # self.lcd.clear(bl=1)
            line1_str = line2_str = line3_str = line4_str = ""
            for i in dataPoints:
                self.log.debug(i)
                # self.lcd.display_string(self.blankline, line)
                disp_str = ""
                # handle GPS data when available
                if i["type"] == "Location":
                    if i["lat"] > 0.0:
                        disp_str = u"GPS: {0:.3f}{1} N {2:.3f}{3} W {4} ".format(i["lat"], ds, i["lon"], ds, i["ele"])
                    else:
                        disp_str = u"GPS: Unknown Unknown Unknown "
                elif i["type"] == "Temperature":
                    disp_str = u"{0}: {1:.2f}{2} {3} ".format(abbr[i["type"]], i["value"], ds, i["symbol"])
                else:
                    disp_str = u"{0}: {1:.2f} {2} ".format(abbr[i["type"]], i["value"], i["symbol"])

                # add to correct line string array
                if i["type"] == "Location":
                    line1_str = u"GPS: {0:.3f}{1} N {2:.3f}{3} W {4}".format(i["lat"], ds, i["lon"], ds, i["ele"])
                elif i["type"] == "Temperature":
                    line2_str += disp_str
                elif i["type"] == "Pressure":
                    line2_str += disp_str
                elif i["type"] == "Relative_Humidity":
                    line2_str += disp_str
                elif i["type"] == "Light_Level":
                    line3_str += disp_str
                elif i["type"] == "Light_Level_lux":
                    line3_str += disp_str
                elif i["type"] == "Volume":
                    line3_str += disp_str
                else:
                    line4_str += disp_str
                # display data on LCD panel
                # self.lcd.display_string(disp_str, line)
                # self.log.debug(u"Display string: {0}, {1}".format(disp_str, line))
                # sleep(0.4)
                # line += 1
                # if line > self.rows:
                #     line = 1
            # update LcdScroller thread data
            self.scroller.updDate((line1_str, line2_str, line3_str, line4_str))
            # self.line1.updData(line1_str)
            # self.line2.updData(line2_str)
            # self.line3.updData(line3_str)
            # self.line4.updData(line4_str)

        except Exception as e:
            self.log.error("Error displaying string on LCD: {0}".format(e))
            raise
        else:
            return True

    def stopScrollers(self):
        self.log.info("Stopping LcdScroller threads")
        if self.scroller.isAlive():
            self.scroller.stopScroller()
            self.scroller.join()
        # if self.line1.isAlive():
        #     self.line1.stopScroller()
        #     self.line1.join()
        # if self.line2.isAlive():
        #     self.line2.stopScroller()
        #     self.line2.join()
        # if self.line3.isAlive():
        #     self.line3.stopScroller()
        #     self.line3.join()
        # if self.line4.isAlive():
        #     self.line4.stopScroller()
        #     self.line4.join()

        self.log.info("Clearing LCD panel & turning off backlight")
        try:
            self.lcd.clear(bl=0)
        except Exception as e:
            self.log.error("Error clearing LCD panel: {0}".format(e))
            raise
