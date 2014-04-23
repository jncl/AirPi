import sensor
import GpsController
from socket import gethostname

# add logging support
import logging
log = logging.getLogger('AirPi')

gpsc = None # define gps data structure
locns = {
    "TS5" : "Middlesbrough",
    "DL12" : "Eggleston",
    "TA1" : "Taunton",
    "CAR" : "Mobile"
}

class GPS(sensor.Sensor):
    requiredData = []
    optionalData = []

    def __init__(self, data):
        self.sensorName = "MTK3339"
        self.valName = "Location"
        self.locnName = locns[gethostname().split("-")[1]]
        # start polling the GPS data
        global gpsc
        try:
            gpsc = GpsController.GpsController()
            # start the controller thread
            gpsc.start()
        except Exception as e:
            print("GPS __init__ Exception: %s" % e)
            log.exception("GPS __init__ Exception %s" % e)
            raise

    def getVal(self):
        global gpsc
        gpsData = [gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude]
        # we're mobile and outside if locnName is "Mobile"
        if self.locnName == "Mobile":
            gpsData.extend(["mobile", "outdoor"])
        else:
            gpsData.extend(["fixed", "indoor"])
        log.debug("GPS data: %s" % str(gpsData))
        return gpsData

    def stopController(self):
        global gpsc
        print("Stopping GPS controller")
        log.info("Stopping GPS controller")
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()
