import sensor
import GpsController
import socket

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
        self.valType = "Location"
        self.locnName = locns[socket.gethostname().split("-")[1]]

        # start polling the GPS data
        global gpsc
        try:
            gpsc = GpsController.GpsController()
            # start the controller thread
            gpsc.start()
        except Exception as e:
            print("GPS __init__ Exception: {0}".format(e))
            log.exception("GPS __init__ Exception: {0}".format(e))
            raise

    def getVal(self):
        global gpsc
        gpsData = [gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "physical"]

        # we're mobile and outside if locnName is "Mobile"
        if self.locnName == "Mobile":
            gpsData.extend(["mobile", "outdoor"])
        else:
            gpsData.extend(["fixed", "indoor"])

        log.debug("GPS data: {0}".format(gpsData))
        return gpsData

    def stopController(self):
        global gpsc
        print("Stopping GPS controller")
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()
