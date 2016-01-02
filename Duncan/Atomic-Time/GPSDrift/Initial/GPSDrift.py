"""
GPSDrift.py
Created: 10/10/2015
Author: Joe Wilson <jw32g12@soton.ac.uk>
"""

import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import math
	
def measureTime( ard ):
	""" Returns the value of the millisecond time difference between GPS updates on Arduino. 
	Inputs:
		ard: Serial stream connection to Arduino
	Returns:
		integer: Milliseconds between last two GPS updates. -1 on failed read.
	"""
	
	try:
		# Get time between last GPS updates
		data = ard.readline().decode()
		data = str(data)
		print (data)

		commaLoc = data.index(',')
		dataT = data[:commaLoc]
		dataF = data[commaLoc+1:]

		valT = 0
		valF = 0

		if (len(dataT)==0):			# convert time1 to integer (can't convert 0 to integer because its string length is 0)
			valT = 0
		else:
			valT = int(dataT)

		if (len(dataF)==0):
			valF = 0
		else:
			valF = int(dataF)

	except serial.SerialTimeoutException:
		return -1
	
	return int(valT), int(valF)
	
def clearBuffer( ard ):
	""" Clears 1024 bytes from 'ard' serial buffer.
	Inputs:
		ard: Serial stream connection to Arduino
	Returns:
		boolean: True on success, False on failure.
	"""
	try:
		ard.read(1024)
	except serial.SerialTimeoutException as err:
		print(err)
		return False
		
	return True

if __name__ == "__main__":

	t_timeout = 2
	ard = None
	N = 3*60*60 # Number of measurements to take (1Hz GPS gives 1 measurement per second)
		
	arduinoTime = np.zeros(N, dtype=np.int)		# stores the time
	fixData = np.zeros(N, dtype=np.int)		# stores the state of the fix
	
	try:
		ard = serial.Serial('COM4', 9600, timeout = t_timeout)
	except serial.SerialException as err:
		print(err)
	

	# If connected
	if ard:
		print("Waiting for Arduino to initialise...")
		# sleep so that the arduino can initialise (it resets upon serial opening)
		time.sleep(3)
		
		print("Clearing serial buffer...")
		clearBuffer( ard )
		
		print("Measuring...\n")
		
		# Do N measurements every t_timePeriod seconds
		for i in range(N):
			arduinoTime[i], fixData[i] = measureTime( ard )
			print(arduinoTime[i])
			
		ard.close()
		
		arduinoTimeStr = [str(i) for i in arduinoTime]
		fixDataStr = [str(i) for i in fixData]
	
	
		text_file = open("{0} GPSDrift_measurements.txt".format(datetime.now().strftime("%H%M%S %d%m%Y")), "w")
		
		for i in range (N):
			text_file.write(arduinoTimeStr[i])
			text_file.write(" ")
			text_file.write(fixDataStr[i])
			text_file.write("\n")

		text_file.close()


		plt.ylim(0, math.floor(max(arduinoTime) * 1.5))
		plt.plot(range(N), arduinoTime)
		plt.show()
	
	
	