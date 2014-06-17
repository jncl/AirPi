# -*- coding: utf-8 -*-
import sensor
import dhtreader
import time

class DHT22(sensor.Sensor):
	requiredData = ["measurement", "pinNumber"]
	optionalData = ["unit"]
	def __init__(self,data):
		dhtreader.init()
		dhtreader.lastDataTime = 0
		dhtreader.lastData = (None,None)
		self.sensorName = "DHT22"
		self.pinNum = int(data["pinNumber"])
		if "temp" in data["measurement"].lower():
			self.valType = "Temperature"
			self.valUnit = "Celsius"
			self.valSymbol = "C"
			if "unit" in data:
				if data["unit"] == "F":
					self.valUnit = "Fahrenheit"
					self.valSymbol = "F"
		elif "h" in data["measurement"].lower():
			self.valType = "Relative_Humidity"
			self.valSymbol = "%"
			self.valUnit = "% Relative Humidity"
		return

	def getVal(self):
		tm = dhtreader.lastDataTime
		if (time.time() - tm) < 2:
			t, h = dhtreader.lastData
		else:
			try:
				t, h = dhtreader.read(22, self.pinNum)
			except Exception:
				t, h = dhtreader.lastData
			dhtreader.lastData = (t, h)
			dhtreader.lastDataTime = time.time()
		if self.valType == "Temperature":
			temp = t
			if self.valUnit == "Fahrenheit":
				temp = temp * 1.8 + 32
			return temp
		elif self.valType == "Relative_Humidity":
			return h
