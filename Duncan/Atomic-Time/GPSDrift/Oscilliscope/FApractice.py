# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 17:57:27 2015
@author: Duncan

Compute distribution of Serial signal from GPS from average

Measurement of PPS (regular square wave) triggered from start of serial
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import bisect

filename = "isfread\combined_triggerSerial.csv"
pulseStart = 0.0

pulseLen = 0.1				# length of PPS (s)
timeA = np.zeros(0)			# data for averaged PPS
pulseAvg_t = np.zeros(0)	# average of PPS signal in time domain
serialAvg_t = np.zeros(0)	# data for averaged serial
pulseOutline_t = np.zeros(0)	# data for theoretical single pulse

window = np.bartlett 		# windowing function used

# find number of rows

fileTemp = open(filename)
textTemp = fileTemp.read()
row_count = textTemp.count("\n")

# sort data into arrays

with open(filename, newline='\n') as csvfile:
	readFile = csv.reader(csvfile, delimiter=',', quotechar='|')
	timeA = np.zeros(row_count)
	pulseAvg_t = np.zeros(row_count)
	serialAvg_t = np.zeros(row_count)
	pulseOutline_t = np.zeros(row_count)
	i=0
	for row in readFile:
		timeA[i] = float(row[0])
		pulseAvg_t[i] = float(row[1])
		serialAvg_t[i] = float(row[2])
		if (abs(timeA[i]-(pulseStart+pulseLen/2))<pulseLen/2):
			pulseOutline_t[i] = 1
		else:
			pulseOutline_t[i] = 0
		pulseOutline_t[i] = np.cos(1.2*np.pi*timeA[i])
		i+=1
	
dt = (timeA[row_count-1]-timeA[0])/(row_count-1)


## add extra time to arrays so that the mirrored time data doesn't overlap time of interest
#for i in range(row_count):
#	timeA[row_count+i] = timeA[row_count-1]+(i+1)*dt
#	pulseAvg_t[row_count+i] = pulseAvg_t[row_count-1]
#	serialAvg_t[row_count+i] = 0
#	pulseOutline_t[row_count+i] = 0

# array for frequencies
df = 1.0/timeA[-1]
freqA = np.zeros(len(timeA))
for i in range(len(freqA)):
	freqA[i]=i*df
	
pulseOutline_f = np.fft.fft(pulseOutline_t)
pulseOutline_t3 = np.fft.ifft(pulseOutline_f)
	
	
# truncate to f=fHigh
fHigh = 1000
fIndex = min(len(freqA), bisect.bisect_left(freqA, fHigh))

pulseOutline_f2 = pulseOutline_f[:fHigh]
freqA2 = freqA[:fHigh]


# create new time array for truncated data
dt2 = 1/freqA2[-1]


timeA2 = np.zeros(len(freqA2))
for i in range(len(timeA2)):
	timeA2[i]=i*dt2

# Inverse DFT to the time domain

pulseOutline_t2 = np.fft.fft(pulseOutline_f2)

#plt.plot(timeA, pulseOutline_t)
#plt.plot(freqA2, pulseOutline_f2)
#plt.plot(timeA2, abs(pulseOutline_t2))
plt.plot(timeA, (pulseOutline_t3))