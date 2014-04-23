#!/usr/bin/env python

#This file takes in inputs from a variety of sensor files, and outputs information to a variety of services
import sys
sys.dont_write_bytecode = True

import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os
from sys import exit
from math import isnan
from sensors import sensor
from outputs import output

# add logging support
import logging, logging.handlers
LOG_FILENAME = os.path.join("/var/log/airpi" , 'airpi.log')
# Set up a specific logger with our desired output level
log = logging.getLogger('AirPi')
log.setLevel(logging.DEBUG)
# create handler and add it to the log
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes = 40960, backupCount = 5)
log.addHandler(handler)
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

cfgdir = "/usr/local/etc/airpi"
sensorcfg = os.path.join(cfgdir, 'sensors.cfg')
outputscfg = os.path.join(cfgdir, 'outputs.cfg')
settingscfg = os.path.join(cfgdir, 'settings.cfg')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) #Use BCM GPIO numbers.

gpsPluginInstance = None

if not os.path.isfile(settingscfg):
    print("Unable to access config file: settings.cfg")
    log.error("Unable to access config file: %s" % settingscfg)
    exit(1)

if not os.path.isfile(sensorcfg):
    print("Unable to access config file: sensors.cfg")
    log.error("Unable to access config file: %s" % sensorscfg)
    exit(1)

if not os.path.isfile(outputscfg):
    print("Unable to access config file: outputs.cfg")
    log.error("Unable to access config file: %s" % outputscfg)
    exit(1)

def pandl(type, msg, vals=None):
    if vals == None:
        vals = ""
    print(msg % vals)
    if type == "I":
        log.info(msg % vals)
    elif type == "D":
        log.debug(msg % vals)
    elif type == "E":
        log.error(msg % vals)
    elif type == "Ex":
        log.exception(msg % vals)

def get_subclasses(mod, cls):
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj

# Inputs
sensorConfig = ConfigParser.SafeConfigParser()
sensorConfig.read(sensorcfg)
sensorNames = sensorConfig.sections()
sensorPlugins = []

for i in sensorNames:
    try:
        try:
            filename = sensorConfig.get(i,"filename")
        except Exception:
            pandl("Ex", "No filename config option found for sensor plugin %s", vals=i)
            # print("Error: no filename config option found for sensor plugin " + i)
            # log.exception("Error: no filename config option found for sensor plugin %s" % i)
            raise
        try:
            enabled = sensorConfig.getboolean(i,"enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                mod = __import__('sensors.' + filename, fromlist = ['a']) #Why does this work?
            except Exception:
                pandl("Ex", "Could not import sensor module %s", vals=filename)
                # print("Error: could not import sensor module " + filename)
                # log.exception("Error: could not import sensor module %s" % filename)
                raise

            try:
                sensorClass = get_subclasses(mod, sensor.Sensor)
                if sensorClass == None:
                    raise AttributeError
            except Exception:
                pandl("Ex" ,"Could not find a subclass of sensor.Sensor in module %s", vals=filename)
                # print("Error: could not find a subclass of sensor.Sensor in module " + filename)
                # log.exception("Error: could not find a subclass of sensor.Sensor in module %s" % filename)
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

            class MissingField(Exception): pass

            for requiredField in reqd:
                if sensorConfig.has_option(i, requiredField):
                    pluginData[requiredField] = sensorConfig.get(i, requiredField)
                else:
                    pandl("E", "Missing required field %s for sensor plugin %s", vals=(requiredField, i))
                    # print("Error: Missing required field '" + requiredField + "' for sensor plugin " + i)
                    # log.error("Error: Missing required field %s for sensor plugin %s" % (requiredField, i))
                    raise MissingField
            for optionalField in opt:
                if sensorConfig.has_option(i, optionalField):
                    pluginData[optionalField] = sensorConfig.get(i, optionalField)
            instClass = sensorClass(pluginData)
            sensorPlugins.append(instClass)
            # store sensorPlugins array length for GPS plugin
            if i == "GPS":
                gpsPluginInstance = instClass
            pandl("I", "Loaded sensor plugin %s", vals=i)
            # print("Success: Loaded sensor plugin " + i)
            # log.info("Success: Loaded sensor plugin %s" % i)
    except Exception as e: # add specific exception for missing module
        pandl("Ex", "Failed to import sensor plugin %s: [%s]", vals=(i, e))
        # print("Error: Did not import sensor plugin " + i)
        # log.exception("Error: Did not import sensor plugin %s: [%s]" % (i, e))
        raise e

# Outputs
outputConfig = ConfigParser.SafeConfigParser()
outputConfig.read(outputscfg)
outputNames = outputConfig.sections()
outputPlugins = []

for i in outputNames:
    try:
        try:
            filename = outputConfig.get(i, "filename")
        except Exception:
            pandl("Ex", "No filename config option found for output plugin %s", vals=i)
            # print("Error: no filename config option found for output plugin " + i)
            # log.exception("Error: no filename config option found for output plugin %s" % i)
            raise
        try:
            enabled = outputConfig.getboolean(i, "enabled")
        except Exception:
            enabled = True

        #if enabled, load the plugin
        if enabled:
            try:
                mod = __import__('outputs.' + filename, fromlist = ['a']) #Why does this work?
            except Exception:
                pandl("Ex", "Could not import output module %s", vals=filename)
                # print("Error: could not import output module " + filename)
                # log.exception("Error: could not import output module %s" % filename)
                raise

            try:
                outputClass = get_subclasses(mod, output.Output)
                if outputClass == None:
                    raise AttributeError
            except Exception:
                pandl("Ex","Could not find a subclass of output.Output in module %s", vals=filename)
                # print("Error: could not find a subclass of output.Output in module " + filename)
                # log.exception("Error: could not find a subclass of output.Output in module %s" % filename)
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

            class MissingField(Exception): pass

            for requiredField in reqd:
                if outputConfig.has_option(i, requiredField):
                    pluginData[requiredField] = outputConfig.get(i, requiredField)
                else:
                    pandl("E", "Missing required field %s for output plugin %s", vals=(requiredField, i))
                    # print("Error: Missing required field '" + requiredField + "' for output plugin " + i)
                    # log.error("Error: Missing required field %s for output plugin %s" % (requiredField, i))
                    raise MissingField
            for optionalField in opt:
                if outputConfig.has_option(i, optionalField):
                    pluginData[optionalField] = outputConfig.get(i, optionalField)
            instClass = outputClass(pluginData)
            instClass.async = async
            outputPlugins.append(instClass)
            pandl("I", "Loaded output plugin %s", vals=i)
            # print("Success: Loaded output plugin " + i)
            # log.info("Success: Loaded output plugin %s" % i)
    except Exception as e: # add specific exception for missing module
        pandl("Ex", "Failed to import output plugin %s", vals=i)
        # print("Error: Did not import output plugin " + i)
        # log.exception("Error: Did not import output plugin %s" % i)
        raise e


# Main Loop

mainConfig = ConfigParser.SafeConfigParser()
mainConfig.read(settingscfg)

delayTime = mainConfig.getfloat("Main", "uploadDelay")
redPin = mainConfig.getint("Main", "redPin")
greenPin = mainConfig.getint("Main", "greenPin")
GPIO.setup(redPin, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(greenPin, GPIO.OUT, initial = GPIO.LOW)

lastUpdated = 0

while True:
    try:
        curTime = time.time()
        if (curTime - lastUpdated) > delayTime:
            lastUpdated = curTime
            data = []
            #Collect the data from each sensor
            for i in sensorPlugins:
                dataDict = {}
                val = i.getVal()
                if i == gpsPluginInstance:
                    if isnan(val[2]): # this means it has no data to upload.
                        continue
                    log.debug("GPS output: %s" % (val,))
                    # handle GPS data
                    dataDict["latitude"] = val[0]
                    dataDict["longitude"] = val[1]
                    dataDict["altitude"] = val[2]
                    dataDict["disposition"] = val[3]
                    dataDict["exposure"] = val[4]
                    dataDict["location"] = i.locnName
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                else:
                    if val == None: # this means it has no data to upload.
                        continue
                    dataDict["value"] = val
                    dataDict["unit"] = i.valUnit
                    dataDict["symbol"] = i.valSymbol
                    dataDict["name"] = i.valName
                    dataDict["sensor"] = i.sensorName
                data.append(dataDict)
            working = True
            try:
                for i in outputPlugins:
                    working = working and i.outputData(data)
                if working:
                    pandl("I", "Uploaded successfully")
                    # print "Uploaded successfully"
                    # log.info("Uploaded successfully")
                    GPIO.output(greenPin, GPIO.HIGH)
                else:
                    pandl("I", "Failed to upload")
                    # print "Failed to upload"
                    # log.info("Failed to upload")
                    GPIO.output(redPin, GPIO.HIGH)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                pandl("Ex", "Main Loop Exception: %s", vals=e)
                # log.exception("Exception: %s" % e)
            else:
                # delay before turning off LED
                time.sleep(1)
                GPIO.output(greenPin, GPIO.LOW)
                GPIO.output(redPin, GPIO.LOW)
        # wait for remainder of delayTime
        waitTime = (delayTime - (time.time() - lastUpdated)) + 0.01
        if waitTime > 0:
            time.sleep(waitTime)
    except KeyboardInterrupt:
        pandl("I", "KeyboardInterrupt detected")
        # print("KeyboardInterrupt detected")
        # log.info("KeyboardInterrupt detected")
        if gpsPluginInstance:
            gpsPluginInstance.stopController()
        exit(1)
