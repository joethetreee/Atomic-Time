# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

combine dual data files
input1 format:
serial_time,pps_time

input2 format:
list of nmea sentences separated by '\n' including GGA

output format:
serial_time,pps_time,satellite_number
"""

import time
import numpy as np
import matplotlib.pyplot as plt
filenameGPS = "Set-3-DULGPS07"
filenameETH = "Set-3-DULETH13Cor"
filenameOut = "Set-3-Combined"


contentsGPS = open(filenameGPS+".txt", mode='r')
contentsGPSTxt = contentsGPS.readlines()
contentsGPS.close()

contentsETH = open(filenameETH+".txt", mode='r')
contentsETHTxt = contentsETH.readlines()
contentsETH.close()


print("lengths: ",len(contentsGPSTxt),len(contentsETHTxt))
qLen = 0			 	 	# stores length of connection quality array
qArr = [0]*len(contentsGPSTxt)	# store connections quality

# get connection quality for GPS data
for i in range(len(contentsGPSTxt)):
	if (contentsGPSTxt[i][:6]=="$GPGGA"):
		commaLoc = 0
		for commaNum in range(7):
			commaLoc += contentsGPSTxt[i][commaLoc:].index(',')+1
		commaLoc2 = commaLoc+contentsGPSTxt[i][commaLoc:].index(',')
		qVal = int(contentsGPSTxt[i][commaLoc:commaLoc2])
		if (qVal != 0):		# do not want to store no connection data (no timing counterpart)
			qArr[qLen] = qVal
			qLen += 1

qArr = qArr[:qLen]			# remove extra entries

# get running time for Arduino time measurement data	
ser_T = [0]*len(contentsETHTxt)
pps_T = [0]*len(contentsETHTxt)
ser_T = ser_T[:len(ser_T)]
pps_T = pps_T[:len(pps_T)]

j = 0
for i in range(len(ser_T)):
	line = contentsETHTxt[i]
	if (',' in line):
		commaLoc = line.index(',')
		ser_T[j] = int(line[:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1


# write new file
contentsOut = open(filenameOut+".txt", mode='w+')

length = min(len(pps_T), len(ser_T), len(qArr))
pps_o = 0						# offset for pps
ser_o = 0						# offset for ser
qArr_o = 0						# offset for qArr

pps_o = min(pps_o, len(pps_T)-length)	# limit offset if necessary
ser_o = min(ser_o, len(ser_T)-length)	# limit offset if necessary
qArr_o = min(qArr_o, len(qArr)-length)	# limit offset if necessary

for i in range(length):
	contentsOut.write(str(ser_T[ser_o+i])+","+str(pps_T[pps_o+i])+","+str(qArr[qArr_o+i])+"\n")

contentsOut.close()