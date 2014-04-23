import sensor
import GpsController
from socket import gethostname

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
        # start the GPS data polling
        global gpsc
        try:
            gpsc = GpsController.GpsController()
            # start controller
            gpsc.start()
        # Error
        except Exception as e:
            print "Exception:", e
            raise

    def getVal(self):
        global gpsc
        # we're mobile and outside if locnName is "Mobile"
        if self.locnName == "Mobile":
            return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "mobile", "outdoor")
        else:
            return (gpsc.fix.latitude, gpsc.fix.longitude, gpsc.fix.altitude, "fixed", "indoor")

    def stopController(self):
        global gpsc
        print "Stopping gps controller"
        gpsc.stopController()
        # wait for the thread to finish
        gpsc.join()
