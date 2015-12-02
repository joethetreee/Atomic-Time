# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot based on number of satellites
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from colour import Color
from scipy.stats.stats import pearsonr
filename = "Set-3-Combined"
normalise = False

def ColArray(N):
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours
	

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

#contentsTxt = contentsTxt[1000:5000]

print("length: ",len(contentsTxt))
ser_T = [0]*len(contentsTxt)	 	# store serial times
pps_T = [0]*len(contentsTxt)	 	# store pps times
qArr = [0]*len(contentsTxt)	 	# store connections quality

# put data into arrays
j=0
for i in range(len(ser_T)):
	line = contentsTxt[i]
	if (',' in line):
		commaLoc0 = line.index(',')
		commaLoc1 = commaLoc0+1+line[commaLoc0+1:].index(',')
		ser_T[j] = int(line[:commaLoc0])
		pps_T[j] = int(line[commaLoc0+1:commaLoc1])
		qArr[j] = int(line[commaLoc1+1:])
		j += 1

# find quality types in data
qTypes = []
for i in range(len(qArr)):
	if (qArr[i] not in qTypes):
		qTypes.append(qArr[i])

# put data into arrays of arrays
dataComb = [[[] for i in range(3)] for j in range(len(qTypes))] 		# array of dual arrays; store ser,pps,second for each qVal

for i in range(len(qArr)):
	qVal = qArr[i]
	qI = qTypes.index(qVal)
	dataComb[qI][0].append(ser_T[i])
	dataComb[qI][1].append(pps_T[i])
	dataComb[qI][2].append(i)								# x values; time in seconds
	
ppsser_dT_ = [[] for i in range(len(dataComb))]
for i in range(len(ppsser_dT_)):
	ppsser_dT_[i] = [0]*len(dataComb[i][0])
	for j in range(len(ppsser_dT_[i])):
		ppsser_dT_[i][j] = dataComb[i][0][j]-dataComb[i][1][j]
	
ppsser_dT = [0]*len(ser_T)
for i in range(len(ppsser_dT)):
	ppsser_dT[i] = ser_T[i]-pps_T[i]

colArray = ColArray(len(qTypes))
colA = [0]*len(ppsser_dT)
for i in range(len(colA)):
	colA[i] = rgb=colArray[qTypes.index(qArr[i])][:3]
	
qTypesN = [0]*len(qTypes)
qArrN = [0]*len(qArr)
qMax = max(qTypes)
for i in range(len(qTypes)):
	qTypesN[i] = qTypes[i]/qMax
for i in range(len(qArrN)):
	qArrN[i] = qArr[i]/qMax

binMin = 0
binMax = 1000
binNum = 1000
ser_leg = [0]*len(ppsser_dT)
txt_leg = [str(i) for i in qTypes]
for j in range(len(ppsser_dT_)):
	histData = ppsser_dT_[j]
	binWidth = (binMax - binMin)
	binEdges = np.linspace(binMin, binMax, binNum)
	
	binVals = np.histogram(histData, bins=binEdges)[0]
	binMids = [0]*len(binVals)
	binVals2 = [0.]*len(binVals)
	
	if (normalise):
		tot = sum(binVals)
		for k in range(len(binVals)):
			binVals2[k] = float(binVals[k])/tot
		binVals = binVals2
	
	for i in range(len(binMids)):
		binMids[i] = (binEdges[i]+binEdges[1+i])/2.0
		
	ser_leg[j] ,= plt.plot(binMids, binVals)
	
plt.title("pps-serial dT dist by # of satellites")
plt.xlabel("dt /ms")
plt.ylabel("frequency")
plt.legend(ser_leg, txt_leg)
plt.show()