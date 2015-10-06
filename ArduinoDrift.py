"""
ArduinoDrift.py
Created: 04/10/2015
Author: Joe Wilson <jw32g12@soton.ac.uk>
"""

import time
import serial
import numpy as np
import subprocess

def startClock( ard ):
	""" Initiates timer on Arduino. 
	Inputs:
		ard: Serial stream connection to Arduino
	Returns:
		boolean: False on failed write otherwise True
	""" 
	
	# Instruct the Arduino to start measuring and return its start time
	try:
		ard.write("0\n".encode("ascii"))
	except SerialTimeoutException as err:
		print(err)
		return False
		
	return True
	
def stopClock( ard ):
	""" Stops timer on Arduino. 
	Inputs:
		ard: Serial stream connection to Arduino
	Returns:
		boolean: False on failed read/write, True on successful halt.
	""" 
	
	try:
		# Tell Arduino to finish
		ard.write("2\n".encode("ascii"))
	except SerialTimeoutException as err:
		print(err)
		return False
		
	try:
		# Check if Arduino has complied with request.
		result = ard.readline()
		if result == "OK":
			return True
	except SerialTimeoutException as err:
		print(err)
		
	return False
	
def measureTime( ard ):
	""" Returns the value of the millisecond timer on Arduino. 
	Inputs:
		ard: Serial stream connection to Arduino
	Returns:
		result: Arduino time since start of measurement
		boolean: False on failed read/write
	"""
	
	try:
		# Tell Arduino to return its current timer value.
		ard.write("1\n".encode("ascii"))
	except SerialTimeoutException:
		return False
		
	try:
		# Read Arduino's current timer value as string (can conver to float later for speed).
		result = ard.readline()
		return result
	except SerialTimeoutException as err:
		print(err)
		
	return False
	
	
def syncTime():
	# Sync time
	#subprocess.check_output("w32tm /resync", stderr = subprocess.STDOUT)

	return True

if __name__ == "__main__":

	ard = None
	
	N = 10 # Number of measurements
	T = 60 * 60 # Period between measurements
	
	pcTime = np.zeros(N + 1)
	arduinoTime = np.zeros(N + 1)
	
	try:
		ard = serial.Serial('COM3', 9600, timeout = 1)
	except serial.SerialException as err:
		print(err)
	

	# If connected
	if ard:
		# Synchronise PC time for initial measurement.
		syncTime()
		# Start Arduino timer.
		startClock(ard)
		
		# Do N measurements every T seconds
		for i in N:
			# Synchronise PC time
			syncTime()

			# Get current synchronised PC time
			pcTime[i + 1] = time.time()
			
			# Get currrent Arduino time
			arduinoTime[i + 1] = measureTime(ard)
			
			# Wait for next measurement
			time.sleep(T)
			
			
		# End test measurement
		stopClock(ard)
	
	
	