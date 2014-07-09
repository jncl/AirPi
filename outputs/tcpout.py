# based upon code from http://logic.sysbiol.cam.ac.uk/?p=1423
import output
import socket

# add logging support
import logging
mod_log = logging.getLogger('airpi.tcpout')

class TCPout(output.Output):
    requiredData = ["host", "port"]
    optionalData = []

    def __init__(self,data):
        self.log = logging.getLogger('airpi.tcpout')
        self.host = int(data["host"])
        self.port = int(data["port"])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def outputData(self,dataPoints):
        arr = []
        a = l = z = None
        try:
            for i in dataPoints:
                self.log.debug(i)
                # handle GPS data
                if i["type"] == "Location":
                    l = dict(i)
                    # remove elements not required by Xively
                    del l["type"]
                    del l["sensor"]
                else:
                    arr.append({"id": i["type"], "current_value": i["value"]})

            a = json.dumps({"version": "1.0.0", "datastreams": arr, "location": l})
            self.log.debug("Output string: [{0}], {1}".format(a, len(a)))

            # send data over TCP socket
            self.socket.connect((self.host, self.port))
            z = self.socket.send(a)
            self.socket.close()
            self.log.debug("Bytes sent: {0}".format(z))
        except Exception as e:
            self.log.error("Error during processing: {0}".format(e))
            raise
        else:
            return True
