import mcp3008
import sensor
import math

# add logging support
import logging
mod_log = logging.getLogger('airpi.analogue')

class ConfigError(Exception): pass

class Analogue(sensor.Sensor):
    requiredData = ["adcPin", "measurement", "sensorName"]
    optionalData = ["pullUpResistance", "pullDownResistance"]

    def __init__(self, data):
        self.log = logging.getLogger('airpi.analogue')
        self.adc = mcp3008.MCP3008.sharedClass
        self.adcPin = int(data["adcPin"])
        self.valType = data["measurement"]
        self.sensorName = data["sensorName"]
        self.pullUp, self.pullDown = None, None

        if "pullUpResistance" in data:
            self.pullUp = int(data["pullUpResistance"])
        if "pullDownResistance" in data:
            self.pullDown = int(data["pullDownResistance"])

        if self.pullUp != None and self.pullDown != None:
            print("Please choose whether there is a pull up or pull down resistor for the " + self.valType + " measurement by only entering one of them into the settings file")
            self.log.error("Please choose whether there is a pull up or pull down resistor for the {0} measurement by only entering one of them into the settings file".format(self.valType))
            raise ConfigError

        self.valUnit = "Ohms"
        self.valSymbol = "Ohms"

        if self.pullUp == None and self.pullDown == None:
            self.valUnit = "millvolts"
            self.valSymbol = "mV"

        if self.sensorName == "LDR_lux":
            self.valUnit = "lux"
            self.valSymbol = "lx"

    # voltage in is 3.3
    # full voltage is 1023
    def getVal(self):

        result = self.adc.readADC(self.adcPin)

        if result == 0:
            print("Check wiring for the " + self.sensorName + " measurement, no voltage detected on ADC input " + str(self.adcPin))
            self.log.warning("Check wiring for the {0} measurement, no voltage detected on ADC input {1}".format(self.sensorName, str(self.adcPin)))
            return None

        if result == 1023:
            print("Check wiring for the " + self.sensorName + " measurement, full voltage detected on ADC input " + str(self.adcPin))
            self.log.warning("Check wiring for the {0} measurement, full voltage detected on ADC input {1}".format(self.sensorName, str(self.adcPin)))
            return None

        vout = float(result) / 1023 * 3.3

        if self.pullDown != None:
            # It's a pull down resistor
            resOut = (self.pullDown * 3.3) / vout - self.pullDown
        elif self.pullUp != None:
            resOut = self.pullUp / ((3.3 / vout) - 1)
        else:
            resOut = vout * 1000

        self.log.debug("sensor: {0}, result: {1}, vout: {2}, resOut: {3}".format(self.sensorName, result, vout, resOut))

        # extra calc for lux value
        resOut2 = 0
        if self.sensorName == "LDR_lux":
            # calc used is from here: http://airpi.freeforums.net/post/574/quote/78
            try:
                resOut2 = 5e9 * (math.log10(resOut) ** -12.78)
                self.log.debug("Analogue: lux value #1 {0}".format(resOut2))
            except: pass
            # another calc from here: http://www.edaboard.com/thread278855.html
            try:
                # resOut2 = math.pow((10000 / (resOut * 10)), (4 / 3))
                resOut2 = 10000 / (resOut * 10) ** (4 / 3)
                self.log.debug("Analogue: lux value #2 {0}".format(resOut2))
            except: pass
            # calc used is from here: http://pi.gate.ac.uk/posts/2014/02/25/airpisensors/
            try:
                resOut2 = math.exp((math.log(resOut / 1000) - 4.125) / - 0.6704)
                self.log.debug("Analogue: lux value #3 {0}".format(resOut2))
            except: pass

            resOut = float("%.2f" % resOut2)

        return resOut
