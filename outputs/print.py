# -*- coding: utf-8 -*-
import output
import datetime

class Print(output.Output):
    requiredData = []
    optionalData = []

    def __init__(self, data):
        pass

    def outputData(self, dataPoints):
        print("")
        print("Time: {0}".format(str(datetime.datetime.now())))
        for i in dataPoints:
            if i["type"] == "Location":
                print("GPS info: {0}".format(i,))
            else:
                print("{0}: {1} {2}".format(i["type"], str(i["value"]), i["symbol"]))
        return True
