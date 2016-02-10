# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 21:31:35 2015

@author: Duncan

Estimate second length by looking at distribution width using different second lengths
"""

import numpy as np
import matplotlib.pyplot as plt

def GetSecSer(serA,tavg):
	"""
	serA: array of serial times
	avg: second length
	___
	builds and returns array of serial times past the second grid line
	"""
	secserA = [serA[i]-serA[0]-i*tavg for i in range(len(serA))]
	return secserA

#filename = "GPSMIL33ChckdCor" 	# filename of data do be cast
#binMin = -500
#binMax = 500
#binWidth = 1
#binNum = (binMax-binMin)/binWidth
#binEdges = np.linspace(binMin,binMax,binNum+1)
#binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]
#
# extract data into arrays
#
#contents = open(filename+".txt", mode='r')
#contentsTxt = contents.readlines()
#contents.close()
#
#ser_T = [0]*len(contentsTxt) 	# PPS times for data
#pps_T = [0]*len(contentsTxt) 	# serial times for data
#
#j = 0
#for i in range(len(contentsTxt)):
#	line = contentsTxt[i]
#	if (line[0]=='t'):
#		commaLoc = line.index(',')
#		ser_T[j] = int(line[1:commaLoc])
#		pps_T[j] = int(line[commaLoc+1:])
#		j += 1
#		
#ser_T = ser_T[:2000]
#pps_T = pps_T[:2000]
#secLenA = (pps_T[-1]-pps_T[0])/(len(pps_T)-1)
#
## get second length and find secser_dT
#avgTx = (ser_T[-1]-ser_T[0])/(len(ser_T)-1) 	 	# expected length of second
#avgTu = 150/len(ser_T)					 	 	# uncertainty in length of second

def CalcWidth(data, avg_):
	binMin = -500
	binMax = 500
	binWidth = 1
	binNum = (binMax-binMin)/binWidth
	binEdges = np.linspace(binMin,binMax,binNum+1)
	binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]
	secser_dT = GetSecSer(data, avg_)
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
	
#	plt.plot(binMids,binVals)
#	plt.show()
	
	return (quart_u-quart_l)

def MinimiseWidth(ser_T_):
	
	def GetCentre(x3, y3): 						# quadratic; x3 and y3 are 3-vectors
		numerator = (y3[0]-y3[1])*(x3[2]**2)-(y3[2]-y3[1])*(x3[0]**2)+(y3[2]-y3[0])*(x3[1]**2)
		denominator = (y3[0]-y3[1])*x3[2]-(y3[2]-y3[1])*x3[0]+(y3[2]-y3[0])*x3[1]
		
		if (denominator==0):
			return x3[1]
		return numerator/(2*denominator)
		
	count = 0
	countT = 10
	avgTx = (ser_T_[-1]-ser_T_[0])/(len(ser_T_)-1) 	 	# expected length of second
	avgTu = 150/len(ser_T_)					 	 	# uncertainty in length of second
	avgTuTarget = avgTu/4
	
	secArr = [0,0,0]
	widthArr = [0,0,0]
	
	while(True):
		for i in range(len(widthArr)):
			secArr[i] = avgTx+(i-1)*avgTu
			widthArr[i] = CalcWidth(ser_T_, secArr[i])
		
#		print(secArr)
#		print(widthArr)
		centre_ = GetCentre(secArr, widthArr)
#		print(centre_)
		if (centre_==avgTx and avgTu<=avgTuTarget):
			return (avgTx, widthArr[1])
		if (count == countT):
			return (avgTx, widthArr[1])
		
		if (abs(avgTx-centre_)<avgTu/2):
			avgTx = centre_
			avgTu /= 2
		else:
			avgTx += avgTu * np.sign(centre_-avgTx)
		count += 1

#print(MinimiseWidth(ser_T))
#print(secLenA)