# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 14:13:51 2016

@author: Duncan

Receive Arduino data and save to txt file
"""

import serial
import time

filenamePrefix = "GARNMEA"
failT = 3
failC = 0

	
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

t_timeout = 3
ard = None

try:
	ard = serial.Serial('COM3', 9600, timeout = t_timeout)
except serial.SerialException as err:
	print(err)

# If connected
if ard:
	print("Waiting for Arduino to initialise...")
	# sleep so that the arduino can initialise (it resets upon serial opening)
	
	filename = filenamePrefix+time.strftime("%Y%m%d")+"_"+time.strftime("%H%M%S")
	file = open(filename+".txt","w")
	
	print("created file")
	
	print("Clearing serial buffer...")
	clearBuffer( ard )
	
	print("Measuring...\n")
	
	while (True):
		try:
			data = ard.readline().decode()
			data = str(data[:-1])
		except UnicodeDecodeError:
			data = "Decoding error"
			
		print (data)
		file.write(data)
		file.write("\n")
		if (len(data)<2):
			failC += 1
			print("failed: ", data)
			if (len(data)>0):
				print("->",int(data[0]))
			ard.close()
			try:
				ard = serial.Serial('COM3', 9600, timeout = t_timeout)
			except serial.SerialException as err:
				ard.close()
				file.close()
				print(err)
		else: failC = 0
		if (failC>=failT): break
	print("Closing")
	ard.close()
		
	file.close()


