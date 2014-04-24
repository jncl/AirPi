import sensor
import GpsController
import socket

# add logging support
import logging
mod_log = logging.getLogger('airpi.serial_gps')

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

    def __init__(self, data):
        self.log = logging.getLogger('airpi.serial_gps')
        self.sensorName = "MTK3339"
        self.valType = "Location"
        self.locnName = locns[socket.gethostname().split("-")[1]]

        # start polling the GPS data
        try:
            self.gpsc = GpsController.GpsController()
            # start the controller thread
            self.gpsc.start()
        except Exception as e:
            self.log.error("GPS __init__ Exception: {0}".format(e))
            raise

    def getVal(self):
        gpsData = [self.gpsc.fix.latitude, self.gpsc.fix.longitude, self.gpsc.fix.altitude, "physical"]

        # we're mobile and outside if locnName is "Mobile"
        if self.locnName == "Mobile":
            gpsData.extend(["mobile", "outdoor"])
        else:
            gpsData.extend(["fixed", "indoor"])

        self.log.debug("GPS data: {0}".format(gpsData))
        return gpsData

    def stopController(self):
        print("Stopping GPS controller")
        self.log.info("Stopping GPS controller")
        self.gpsc.stopController()
        # wait for the thread to finish
        self.gpsc.join()
