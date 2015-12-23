# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:31:35 2015

@author: Duncan

Estimate second length by looking at distribution width using different second lengths
"""

import numpy as np
import matplotlib.pyplot as plt
import KalmanFilter as klm



def GetSecSer(serA,tavg):
	"""
	serA: array of serial times
	avg: second length
	___
	builds returns array of serial times past the second grid line
	"""
	secserA = [serA[i]-serA[0]-i*tavg for i in range(len(serA))]
	return secserA

filename = "GPSMIL33ChckdCor" 	# filename of data do be cast
binMin = -1000
binMax = 1000
binWidth = 1
binNum = (binMax-binMin)/binWidth
binEdges = np.linspace(binMin,binMax,binNum+1)
binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]

secNum = 6 			# number of second lengths to try on each side of initial estimate

# extract data into arrays

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt) 	# PPS times for data
pps_T = [0]*len(contentsTxt) 	# serial times for data

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:2000]
pps_T = pps_T[:2000]
secLenA = (pps_T[-1]-pps_T[0])/(len(pps_T)-1)

# get second length and find secser_dT
avgTx = (ser_T[-1]-ser_T[0])/(len(ser_T)-1) 	 	# expected length of second
avgTu = 150/len(ser_T)					 	 	# uncertainty in length of second

for i in range(-secNum,secNum+1,1):
	secLenP = avgTx+i*avgTu/10
	secser_dT = GetSecSer(ser_T,avgTx+i*avgTu/10)
	# get template distribution
	binVals = np.histogram(secser_dT, bins=binEdges)[0]
	# normalise
	binVals = [binVals[i]/(sum(binVals)*binWidth) for i in range(len(binVals))]
	
	binCumVals = [binVals[0]]*len(binVals)
	for i in range(1,len(binVals)):
		binCumVals[i] = binCumVals[i-1] + binVals[i]
		
	quart_l = 0
	quart_u = 0
	for i in range(len(binCumVals)):
		if (binCumVals[i] >= 0.25):
			quart_l = i
			break
	for i in range(len(binCumVals)):
		if (binCumVals[i]>=0.75):
			quart_u = i
			break
	
	print("width",quart_u-quart_l,secLenP,(secLenA-secLenP)*(len(secser_dT)-1))
	
#	plt.plot(binMids,binVals)
#	plt.show()


