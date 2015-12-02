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
pulseLen = 0.1				# length of PPS (s)
timeA = []
pulseAvg_t = []				# average of PPS signal in time domain
serialAvg_t = []
pulseOutline_t = []

# sort data into arrays
with open(filename, newline='\n') as csvfile:
	readFile = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in readFile:
		timeA.append(float(row[0]))
		pulseAvg_t.append(float(row[1]))
		serialAvg_t.append(float(row[2]))
		if (timeA[-1]<pulseLen):
			pulseOutline_t.append(1)
		else:
			pulseOutline_t.append(0)
		

# array for frequencies
df = 1.0/timeA[-1]
freqA = np.zeros(len(timeA))
for i in range(len(freqA)):
	freqA[i]=i*df

pulseAvg_f = np.fft.fft(pulseAvg_t)
#plt.plot(pulseAvg_f)

pulseOutline_f = np.fft.fft(pulseOutline_t)
#plt.plot(freqA[:100], pulseOutline_f[:100])

serialAvg_f = np.fft.fft(serialAvg_t)
#plt.plot(serialAvg_f)


# truncate to f=fHigh
fHigh = 200
fIndex = bisect.bisect_left(freqA, fHigh)

dist_f = np.zeros(fIndex)

for i in range(fIndex):
	dist_f[i] = pulseAvg_f[i]/pulseOutline_f[i]
	
dist_t = np.fft.fft(dist_f)

plt.plot(timeA[:len(dist_t)], dist_t)


#dist_f = np.zeros(len(freqA))
#
#for i in range(len(dist_f)):
#	dist_f[i] = pulseAvg_f[i]/pulseOutline_f[i]
#	
#dist_t = np.fft.fft(dist_f)
#
#plt.plot(abs(dist_f[:1000]))