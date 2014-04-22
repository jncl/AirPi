#!/usr/bin/env python

import output
import datetime

class Print(output.Output):
    requiredData = []
    optionalData = []
    def __init__(self, data):
        pass
    def outputData(self, dataPoints):
        print ""
        print "Time: " + str(datetime.datetime.now())
        for i in dataPoints:
            if i["name"] == "Location":
                print("GPS info: %s" % (i,))
            else:
                print i["name"] + ": " + str(i["value"]) + " " + i["symbol"]
        return True