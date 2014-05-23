#!/usr/bin/env python

#This file takes in inputs from a variety of sensor files, and outputs information to a variety of services

import sys
sys.dont_write_bytecode = True
import os
from subprocess import Popen

# add logging support
import logging, logging.handlers
log = logging.getLogger('airpi')
logfile = os.path.join("/var/log/airpi" , 'airpi.log')
# create handler and add it to the log
handler = logging.handlers.RotatingFileHandler(logfile, maxBytes = 40960, backupCount = 5)
log.addHandler(handler)
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import platform

from math import isnan
from sensors import sensor
from outputs import output

debugMode = False

# configuration files
cfgdir      = "/usr/local/etc/airpi"
settingscfg = os.path.join(cfgdir, 'settings.cfg')
sensorscfg  = os.path.join(cfgdir, 'sensors.cfg')
outputscfg  = os.path.join(cfgdir, 'outputs.cfg')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #Use BCM GPIO numbers.

def get_subclasses(mod, cls):
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj

class MissingField(Exception): pass

# Inputs
sensorPlugins = []
gpsPluginInstance = None
def getInputs():

    global gpsPluginInstance # required as updated here

    sensorConfig = ConfigParser.SafeConfigParser()
    sensorConfig.read(sensorscfg)
    sensorNames = sensorConfig.sections()

    for i in sensorNames:
        try:
            try:
                filename = sensorConfig.get(i, "filename")
            except Exception:
                log.error("No filename config option found for sensor plugin {0}".format(i))
                raise
            try:
                enabled = sensorConfig.getboolean(i, "enabled")
            except Exception:
                enabled = True

            # if enabled, load the plugin
            if enabled:
                try:
                    mod = __import__('sensors.' + filename, fromlist = ['a']) #Why does this work?
                except Exception:
                    log.error("Could not import sensor module {0}".format(filename))
                    raise
                # if debugging reload the module, to force changed code to be loaded
                if debugMode:
                    try:
                        mod = reload(mod)
                        log.debug("Reloaded sensor module {0}".format(filename))
                    except NameError:
                        log.error("Could not reload sensor module {0}".format(filename))
                        raise

                try:
                    sensorClass = get_subclasses(mod, sensor.Sensor)
                    if sensorClass == None:
                        raise AttributeError
                except Exception:
                    log.error("Could not find a subclass of sensor.Sensor in module {0}".format(filename))
                    raise

                try:
                    reqd = sensorClass.requiredData
                except Exception:
                    reqd = []
                try:
                    opt = sensorClass.optionalData
                except Exception:
                    opt = []

                pluginData = {}

                for requiredField in reqd:
                    if sensorConfig.has_option(i, requiredField):
                        pluginData[requiredField] = sensorConfig.get(i, requiredField)
                    else:
                        log.error("Missing required field {0} for sensor plugin {1}".format(requiredField, i))
                        raise MissingField

                for optionalField in opt:
                    if sensorConfig.has_option(i, optionalField):
                        pluginData[optionalField] = sensorConfig.get(i, optionalField)

                instClass = sensorClass(pluginData)
                sensorPlugins.append(instClass)
                # store sensorPlugins object for GPS plugin
                if i == "GPS":
                    gpsPluginInstance = instClass
                log.info("Loaded sensor plugin {0}".format(i))
        except Exception:
            log.error("Failed to load sensor plugin {0}".format(i))
            raise

# Outputs
outputPlugins = []
def getOutputs():

    outputConfig = ConfigParser.SafeConfigParser()
    outputConfig.read(outputscfg)
    outputNames = outputConfig.sections()

    for i in outputNames:
        try:
            try:
                filename = outputConfig.get(i, "filename")
            except Exception:
                log.error("No filename config option found for output plugin {0}".format(i))
                raise
            try:
                enabled = outputConfig.getboolean(i, "enabled")
            except Exception:
                enabled = False

            # if enabled, load the plugin
            if enabled:
                try:
                    mod = __import__('outputs.' + filename, fromlist = ['a']) #Why does this work?
                except Exception:
                    log.error("Could not import output module {0}".format(filename))
                    raise
                # if debugging reload the module, to force changed code to be loaded
                if debugMode:
                    try:
                        mod = reload(mod)
                        log.debug("Reloaded output module {0}".format(filename))
                    except NameError:
                        log.error("Could not reload output module {0}".format(filename))
                        raise

                try:
                    outputClass = get_subclasses(mod, output.Output)
                    if outputClass == None:
                        raise AttributeError
                except Exception:
                    log.error("Could not find a subclass of output.Output in module {0}".format(filename))
                    raise
                try:
                    reqd = outputClass.requiredData
                except Exception:
                    reqd = []
                try:
                    opt = outputClass.optionalData
                except Exception:
                    opt = []

                if outputConfig.has_option(i, "async"):
                    async = outputConfig.getbool(i, "async")
                else:
                    async = False

                pluginData = {}

                for requiredField in reqd:
                    if outputConfig.has_option(i, requiredField):
                        pluginData[requiredField] = outputConfig.get(i, requiredField)
                    else:
                        log.error("Missing required field {0} for output plugin {1}".format(requiredField, i))
                        raise MissingField

                for optionalField in opt:
                    if outputConfig.has_option(i, optionalField):
                        pluginData[optionalField] = outputConfig.get(i, optionalField)

                instClass = outputClass(pluginData)
                instClass.async = async
                outputPlugins.append(instClass)
                log.info("Loaded output plugin {0}".format(i))
        except Exception:
            log.error("Failed to load output plugin: {0}".format(i))
            raise

# handle GPIO actuated shutdown
# code based on: http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-2
def shutdownNow(pin):
    print("shutdownNow triggered: {0}".format(pin))
    log.info("shutdownNow triggered: {0}".format(pin))
    Popen('/usr/bin/exitcheck.sh shutdown', shell=True) # shutdown system
    sys.exit(1)

# Main Loop
def getData():

    mainConfig = ConfigParser.SafeConfigParser()
    mainConfig.read(settingscfg)

    cycleCount = mainConfig.getint("Main", "cycleCount")
    delayTime  = mainConfig.getfloat("Main", "uploadDelay")
    redPin     = mainConfig.getint("Main", "redPin")
    greenPin   = mainConfig.getint("Main", "greenPin")

    GPIO.setup(redPin, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(greenPin, GPIO.OUT, initial = GPIO.LOW)
    # handle shutdownPin, if used
    try:
        shutdownPin = mainConfig.getint("Main", "shutdownPin")
        if shutdownPin:
            log.debug("shutdownPin selected {0}".format(shutdownPin))
            # GPIO pin set as input. It is pulled up to stop false signals
            GPIO.setup(shutdownPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # add event to detect when shutdown required
            GPIO.add_event_detect(shutdownPin, GPIO.FALLING, callback=shutdownNow, bouncetime=500)
    except:
        pass

    lastUpdated = curCount = 0

    try:
        while True:

            curTime = time.time()

            if (curTime - lastUpdated) > delayTime:
                lastUpdated = curTime

                # check to see if date is set
                log.debug("Current Time: {0}".format(curTime))
                if curTime < 5000:
                    if gpsPluginInstance != None:
                        gpsPluginInstance:setTime()
                    else:
                        Popen('/etc/init.d/settime.sh', shell=True)
                    continue

                data = []

                #Collect the data from each sensor
                for i in sensorPlugins:
                    dataDict = {}
                    val = i.getVal()
                    if i == gpsPluginInstance:
                        if isnan(val[2]): # this means it has no data to upload.
                            continue
                        # handle GPS data
                        dataDict["lat"]         = val[0]
                        dataDict["lon"]         = val[1]
                        dataDict["ele"]         = val[2]
                        dataDict["domain"]      = val[3]
                        dataDict["disposition"] = val[4]
                        dataDict["exposure"]    = val[5]
                        dataDict["name"]        = i.locnName
                        dataDict["type"]        = i.valType
                        dataDict["sensor"]      = i.sensorName
                    else:
                        if val == None: # this means it has no data to upload.
                            continue
                        dataDict["value"]  = val
                        dataDict["unit"]   = i.valUnit
                        dataDict["symbol"] = i.valSymbol
                        dataDict["type"]   = i.valType
                        dataDict["sensor"] = i.sensorName
                    data.append(dataDict)

                # bail out if no sensor data found
                log.debug("getData after inputs loop: {0} {1}".format(data, len(data)))
                if len(data) == 0:
                    log.error("No Sensor data found, stopping")
                    raise EOFError

                working = True
                try:
                    for i in outputPlugins:
                        working = working and i.outputData(data)
                    if working:
                        log.info("Data output successfully")
                        GPIO.output(greenPin, GPIO.HIGH)
                    else:
                        log.info("Data output unsuccessful")
                        GPIO.output(redPin, GPIO.HIGH)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    log.error("Main Loop Exception: {0}".format(e))
                    raise
                else:
                    # delay before turning off LED
                    time.sleep(1)
                    GPIO.output(greenPin, GPIO.LOW)
                    GPIO.output(redPin, GPIO.LOW)

            # check to see if running a cycle
            # if so then shutdown when cycle has completed
            if cycleCount > 0:
                curCount += 1
                log.debug("cycleCount {0}, curCount {1}".format(cycleCount, curCount))
                if cycleCount == curCount:
                    shutdownNow(99)

            # wait for remainder of delayTime
            waitTime = (delayTime - (time.time() - lastUpdated)) + 0.01
            if waitTime > 0:
                time.sleep(waitTime)

    except KeyboardInterrupt:
        log.debug("KeyboardInterrupt detected")
    except Exception as e:
        log.error("Unexpected Exception {0}".format(e))
        raise

def runAirPi():

    global debugMode # required as updated here

    # set log message level
    log.setLevel(logging.INFO)
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d":
            log.setLevel(logging.DEBUG)
            debugMode = True

    log.info(">>>>>>>> AirPi starting <<<<<<<<")
    log.info("Python Info: {0} - {1} - {2}\n{3}\nDebug Mode: {4}".format(platform.platform(), platform.python_version(), platform.python_build(), str(platform.uname()), debugMode))

    try:
        if not os.path.isfile(settingscfg):
            raise IOError("Unable to access config file: {0}".format(settingscfg))

        if not os.path.isfile(sensorscfg):
            raise IOError("Unable to access config file: {0}".format(sensorscfg))

        if not os.path.isfile(outputscfg):
            raise IOError("Unable to access config file: {0}".format(outputscfg))

        log.debug("Getting Inputs")
        getInputs()
        log.debug("Getting Outputs")
        getOutputs()
        log.debug("Getting Data")
        getData()
    except Exception:
        raise
    finally:
        # stop gps controller
        if gpsPluginInstance != None:
            gpsPluginInstance.stopController()

def main():

    try:
        try:
            runAirPi()
        except Exception:
            log.exception("AirPi Exception:")
            sys.exit(1)
    finally:
        # Shutdown the logging system
        logging.shutdown()
        # Exit here
        os._exit(0)

if __name__ == "__main__":
    main()
