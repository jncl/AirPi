# based upon code from http://logic.sysbiol.cam.ac.uk/?p=1423
import output
import socket
import errno, time

# add logging support
import logging
mod_log = logging.getLogger('airpi.tcpout')

class TCPout(output.Output):
    requiredData = ["host", "port"]
    optionalData = []

    def __init__(self,data):
        self.log = logging.getLogger('airpi.tcpout')
        self.host = data["host"]
        self.port = int(data["port"])

    def outputData(self,dataPoints):
        arr = []
        datastr = ""
        s = z = None
        try:
            for i in dataPoints:
                self.log.debug(i)
                datastr += ','.join("{!s}={!r}".format(k, v) for (k, v) in i)

            self.log.debug("Output string: [{0}], {1}".format(datastr, len(datastr)))

            # send data over TCP socket
            cnt = 0
            while cnt < 3:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.host, self.port))
                    z = s.send(datastr)
                    s.close()
                    self.log.debug("Bytes sent: {0}".format(z))
                except socket.error as e:
                    if e.errno == errno.ECONNREFUSED:
                        time.sleep(0.5)
                        cnt += 1
                    else:
                        raise
                else:
                    cnt = 99

        except Exception as e:
            self.log.error("Error during processing: {0}".format(e))
            raise
        else:
            return True
