# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

check length, times of dual data files
"""

import time
import numpy as np
import matplotlib.pyplot as plt
filenameGPS = "Set-3-DULGPS07"
filenameETH = "Set-3-DULETH13"


contentsGPS = open(filenameGPS+".txt", mode='r')
contentsGPSTxt = contentsGPS.readlines()
contentsGPS.close()

contentsETH = open(filenameETH+".txt", mode='r')
contentsETHTxt = contentsETH.readlines()
contentsETH.close()

# convert HHMMSS to number of seconds since start of day
def ConvertHHMMSS_s(t_H):
	t_s = 0
	t_s += int(t_H[0:2])*60*60
	t_s += int(t_H[2:4])*60
	t_s += int(float(t_H[4:]))
	return t_s


print("lengths: ",len(contentsGPSTxt),len(contentsETHTxt))

# get time range for GPS data
ti=0						# initial time
tf=0						# final time
for i in range(len(contentsGPSTxt)):
	if (contentsGPSTxt[i][:6]=="$GPGGA"):
		commaLoc = 0
		for commaNum in range(1):
			commaLoc += contentsGPSTxt[i][commaLoc:].index(',')+1
		commaLoc2 = commaLoc+contentsGPSTxt[i][commaLoc:].index(',')
		ti = contentsGPSTxt[i][commaLoc:commaLoc2]
		break
		
for i in range(len(contentsGPSTxt)-1,0,-1):
	if (contentsGPSTxt[i][:6]=="$GPGGA"):
		commaLoc = 0
		for commaNum in range(1):
			commaLoc += contentsGPSTxt[i][commaLoc:].index(',')+1
		commaLoc2 = commaLoc+contentsGPSTxt[i][commaLoc:].index(',')
		tf = contentsGPSTxt[i][commaLoc:commaLoc2]
		break

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
		
timeRunGPS = ConvertHHMMSS_s(tf)-ConvertHHMMSS_s(ti)+60*60*24
timeRunETH = (pps_T[-1]-pps_T[0])/1000

print(pps_T[0],pps_T[-1])

print("running time: ",timeRunGPS,timeRunETH)