import sensor
import GpsController
import socket

# add logging support
import logging

locns = {
    "TS5" : "Middlesbrough",
    "DL12" : "Eggleston",
    "TA1" : "Taunton",
    "CAR" : "Mobile"
}

class GPS(sensor.Sensor):
    requiredData = []
    optionalData = []
    gpsc = None
    log = logging.getLogger('airpi')

    def __init__(self, data):
        self.sensorName = "MTK3339"
        self.valType = "Location"
        self.locnName = locns[socket.gethostname().split("-")[1]]

        # start polling the GPS data
        try:
            self.gpsc = GpsController.GpsController()
            # start the controller thread
            self.gpsc.start()
        except Exception as e:
            log.error("GPS __init__ Exception: {0}".format(e))
            raise

    def getVal(self):
        gpsData = [self.gpsc.fix.latitude, self.gpsc.fix.longitude, self.gpsc.fix.altitude, "physical"]

        # we're mobile and outside if locnName is "Mobile"
        if self.locnName == "Mobile":
            gpsData.extend(["mobile", "outdoor"])
        else:
            gpsData.extend(["fixed", "indoor"])

        log.debug("GPS data: {0}".format(gpsData))
        return gpsData

    def stopController(self):
        print("Stopping GPS controller")
        log.info("Stopping GPS controller")
        self.gpsc.stopController()
        # wait for the thread to finish
        self.gpsc.join()
