import output
import os
import datetime
import sqlite3
import json

# add logging support
import logging
log = logging.getLogger('airpi')

class Database(output.Output):
    requiredData = ["dbPath"]
    optionalData = []
    dbName = None
    
    def __init__(self, data):
        self.dbName = os.path.join(data["dbPath"], 'airpi.db')

        try:
            conn = sqlite3.connect(dbName)
             # create table
            conn.execute("CREATE TABLE airpi (timestamp, sensor_data, gps_data)")
            # save changes
            conn.commit()
            # close the connection
            conn.close()
        except sqlite3.OperationalError as oe:
            if "already exists" in oe.message:
                pass
            else:
                log.error("Database OperationalError Exception: {0} - {1}".format(oe, self.dbName))
                raise
        except Exception as e:
            log.error("Database create Exception: {0} - {1}".format(e, self.dbName))
            raise

    def outputData(self, dataPoints):
        arr = []
        sData = lData = None

        for i in dataPoints:
            # handle GPS data
            if i["type"] == "Location":
                lData = json.dumps(i)
            else:
                arr.append(i)

        sData = json.dumps(arr)
        log.debug("Database input: [{0},{1}]".format(sData, lData))

        try:
            conn = sqlite3.connect(self.dbName)
            # add row to table
            conn.execute("insert into airpi values (?, ?, ?)", (str(datetime.datetime.now()), sData, lData))
            # save changes
            conn.commit()
            # close the connection
            conn.close()
        except Exception as e:
            log.error("Database insert Exception: {0}".format(e))
            raise
        else:
            return True
