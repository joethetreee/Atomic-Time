"""
ArduinoDrift.py
Created: 04/10/2015
Author: Joe Wilson <jw32g12@soton.ac.uk>
"""

t_timeout = 0.5
t_timePeriod = 10
t_num = 10

import time
import serial
import numpy as np
import subprocess
import matplotlib.pyplot as plt

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
	except serial.SerialTimeoutException as err:
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
	except serial.SerialTimeoutException as err:
		print(err)
		return False
		
	try:
		# Check if Arduino has complied with request.
		result = ard.readline()
		if result == "OK":
			return True
	except serial.SerialTimeoutException as err:
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
		ard.write("1".encode("ascii"))
	except serial.SerialTimeoutException:
		return False

		
#	try:
##		# Read Arduino's current timer value as string (can convert to float later for speed).
##		result = int(ard.readline().decode("ASCII"))
##		print (result)
##		return result
#
#		# Read Arduino's current timer value as string (can convert to float later for speed).
#		result = ard.readline()
#		
#		print (result)
#		return 0
#
#	except serial.SerialTimeoutException as err:
#		print(err)

	result = -1
	res_raw = ard.readline()
		
	res_raw1 = str(res_raw.decode("ascii"))
	res_raw1 = res_raw1[:len(res_raw1)-1]
	result = int(res_raw1)
		
	return result
	
	
def syncTime():
	# Sync time
	#subprocess.check_output("w32tm /resync", stderr = subprocess.STDOUT)

	return True

if __name__ == "__main__":

	ard = None
		
	pcTime = np.zeros(t_num)
	arduinoTime = np.zeros(t_num)
	
	try:
		ard = serial.Serial('COM3', 9600, timeout = t_timeout)
	except serial.SerialException as err:
		print(err)
	

	# If connected
	if ard:
		# Synchronise PC time for initial measurement.
		syncTime()
		# Start Arduino timer.

		# sleep so that the arduino can initialise (it resets upon serial opening)
		time.sleep(3)

		#startClock(ard)

		offset = time.time()
		
		# Do N measurements every t_timePeriod seconds
		for i in range(t_num):
			# Synchronise PC time
			syncTime()

			# Get current synchronised PC time
			pcTime[i] = int(round(1000*(time.time()-offset)))
			
			# Get currrent Arduino time
			arduinoTime[i] = measureTime(ard)
			
			# Wait for next measurement
			time.sleep(t_timePeriod)
			
			
		# End test measurement
		#stopClock(ard)
		ard.close()

		print(pcTime)
		print(arduinoTime)

		plt.plot(pcTime, arduinoTime)
		plt.show()
		
		text_file = open("ArduinoDrift_measurements.txt", "w")

		text_file.write("(pc time /ms) (arduino time /ms)")
		
		for i in range(t_num):
			text_file.write("\n")
			text_file.write(str(int(pcTime[i])))
			text_file.write(" ")
			text_file.write(str(int(arduinoTime[i])))
			
		
		text_file.close()
	
	
	