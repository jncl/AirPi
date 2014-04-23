import output
import os
import datetime
import sqlite3

# add logging support
import logging
log = logging.getLogger('AirPi')

dbName = None

class Database(output.Output):
    requiredData = ["dbPath"]
    optionalData = []

    def __init__(self, data):
        global dbName
        dbName = os.path.join(data["dbPath"], 'airpi.db')
        try:
            conn = sqlite3.connect(dbName)
            try:
                # create table
                conn.execute("CREATE TABLE airpi (timestamp, sensor_data, gps_data)")
                # save changes
                conn.commit()
            except sqlite3.IntegrityError:
                pass
            except Exception as e:
                log.exception("Database create Exception {0}".format(e))
                raise e
        except Exception as e:
            log.exception("Database connect Exception {0}".format(e))
            raise e
        else:
            # close the connection
            conn.close()

    def outputData(self, dataPoints):
        global dbName
        sData = []
        lData = None

        for i in dataPoints:
            # handle GPS data
            if i["name"] == "Location":
                lData = {"disposition": i["disposition"], "name": i["location"], "exposure": i["exposure"], "ele": i["altitude"], "lat": i["latitude"], "lon": i["longitude"], "sensor": i["sensor"]}
            else:
                sData.append({"name": i["name"], "value": i["value"], "unit": i["unit"], "symbol": i["symbol"], "sensor": i["sensor"]})

        log.debug("Database output: [{0}]".format(sData, lData))
        try:
            conn = sqlite3.connect(dbName)
            try:
                # add row to table
                conn.execute("insert into airpi values (?, ?, ?)", (str(datetime.datetime.now()), sData, lData))
                # save changes
                conn.commit()
            except Exception as e:
                log.exception("Database insert Exception {0}".format(e))
                raise e
        except Exception as e:
            log.exception("Database connect Exception: {0}".format(e))
            raise e
        else:
            # close the connection
            conn.close()
            return True
