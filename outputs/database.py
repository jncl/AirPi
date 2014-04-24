import output
import os
import datetime
import sqlite3
import json

# add logging support
import logging

dbName = None

class Database(output.Output):
    requiredData = ["dbPath"]
    optionalData = []

    def __init__(self, data):
        self.log = logging.getLogger(__name__)
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
        except sqlite3.OperationalError as oe:
            if "already exists" in oe.message:
                pass
            else:
                self.log.exception("Database OperationalError Exception {0}: {1}".format(oe, dbName))
                raise
        except Exception as e:
            self.log.exception("Database create Exception {0}: {1}".format(e, dbName))
            raise

    def outputData(self, dataPoints):
        global dbName
        arr = []
        sData = lData = None

        for i in dataPoints:
            # handle GPS data
            if i["type"] == "Location":
                lData = json.dumps(i)
            else:
                arr.append(i)

        sData = json.dumps(arr)
        self.log.debug("Database input: [{0},{1}]".format(sData, lData))
        try:
            conn = sqlite3.connect(dbName)
            # add row to table
            conn.execute("insert into airpi values (?, ?, ?)", (str(datetime.datetime.now()), sData, lData))
            # save changes
            conn.commit()
            # close the connection
            conn.close()
        except Exception as e:
            self.log.exception("Database insert Exception: {0}".format(e))
            raise
        else:
            return True
