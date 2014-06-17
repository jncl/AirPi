# -*- coding: utf-8 -*-
import output
import os
import datetime
import sqlite3
import json

# add logging support
import logging
mod_log = logging.getLogger('airpi.database')

class Database(output.Output):
    requiredData = ["dbPath"]
    optionalData = []
    dbName = None

    def __init__(self, data):
        self.log = logging.getLogger('airpi.database')
        self.dbName = os.path.join(data["dbPath"], 'airpi.db')

        try:
            conn = sqlite3.connect(self.dbName)
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
                self.log.error("Database OperationalError Exception: {0} - {1}".format(oe, self.dbName))
                raise
        except Exception as e:
            self.log.error("Database create Exception: {0} - {1}".format(e, self.dbName))
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
        self.log.debug("Database input: [{0},{1}]".format(sData, lData))

        try:
            conn = sqlite3.connect(self.dbName)
            # add row to table
            conn.execute("insert into airpi values (?, ?, ?)", (str(datetime.datetime.now()), sData, lData))
            # save changes
            conn.commit()
            # close the connection
            conn.close()
        except Exception as e:
            self.log.error("Database insert Exception: {0}".format(e))
            raise
        else:
            return True
