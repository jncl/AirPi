import output
import os
import datetime
import sqlite3
import json

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
             # create table
            conn.execute("CREATE TABLE airpi (timestamp, sensor_data, gps_data)")
            # save changes
            conn.commit()
            # close the connection
            conn.close()
        except sqlite3.IntegrityError:
            pass
        except Exception as e:
            log.exception("Database create Exception {0}: {1}".format(e, dbName))
            raise e

    def outputData(self, dataPoints):
        global dbName
        arr = []
        sData = lData = None

        for i in dataPoints:
            # handle GPS data
            if i["name"] == "Location":
                lData = json.dumps({"disposition": i["disposition"], "name": i["location"], "exposure": i["exposure"], "ele": i["altitude"], "lat": i["latitude"], "lon": i["longitude"], "sensor": i["sensor"]})
            else:
                arr.append({"name": i["name"], "value": i["value"], "unit": i["unit"], "symbol": i["symbol"], "sensor": i["sensor"]})

        sData = json.dumps(arr)
        log.debug("Database input: [{0},{1}]".format(sData, lData))
        try:
            conn = sqlite3.connect(dbName)
            # add row to table
            conn.execute("insert into airpi values (?, ?, ?)", (str(datetime.datetime.now()), sData, lData))
            # save changes
            conn.commit()
            # close the connection
            conn.close()
        except Exception as e:
            log.exception("Database insert Exception: {0}".format(e))
            raise e
        else:
            return True
