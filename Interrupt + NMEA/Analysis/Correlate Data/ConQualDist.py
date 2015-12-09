# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot based on number of satellites
"""

import numpy as np
import matplotlib.pyplot as plt
filename = "GPSMIL33ChckdCor"
normalise = False

oset_GGA = 0 				# offset of GGA sentence
oset_PPS = 2 				# offset of PPS sentence
period = 3	 				# number of lines in each data set
qCommaIndex = 7				# number of commas in GGA line before data


def ColArray(N):
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours
	

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

print("length: ",len(contentsTxt))
ser_T = [0]*int(np.ceil(len(contentsTxt)/period))	 	# store serial times
pps_T = [0]*int(np.ceil(len(contentsTxt)/period))	 	# store pps times
qArr = [0]*int(np.ceil(len(contentsTxt)/period))	 	# store connections quality
print("~",int(np.ceil(len(contentsTxt)/period)))

# put data into arrays
for i in range(0,len(contentsTxt),period):
	# get information from GGA sentence
	commaLoc = 0
	for commaNum in range(qCommaIndex): 	 	 	# value of interest
		commaLoc += contentsTxt[i+oset_GGA][commaLoc:].index(',')+1
	commaLoc2 = commaLoc + contentsTxt[i+oset_GGA][commaLoc:].index(',')
	qArr[int(i/period)] = int(float(contentsTxt[i+oset_GGA][commaLoc:commaLoc2]))
	
	
	# get information from PPS sentence
	commaLoc = 0
	for commaNum in range(1): 	 	 	 	 	# find pps value
		commaLoc += contentsTxt[i+oset_PPS][commaLoc:].index(',')
	ser_T[int(i/period)] = int(contentsTxt[i+oset_PPS][1:commaLoc])
	pps_T[int(i/period)] = int(contentsTxt[i+oset_PPS][commaLoc+1:])

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
	
#ppsser_dT = [[] for i in range(len(dataComb))]
#for i in range(len(ppsser_dT)):
#	ppsser_dT[i] = [0]*len(dataComb[i][0])
#	for j in range(len(ppsser_dT[i])):
#		ppsser_dT[i][j] = dataComb[i][0][j]-dataComb[i][1][j]
	
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
	
ppsser_dT_ = [[] for i in range(len(dataComb))]
for i in range(len(ppsser_dT_)):
	ppsser_dT_[i] = [0]*len(dataComb[i][0])
	for j in range(len(ppsser_dT_[i])):
		ppsser_dT_[i][j] = dataComb[i][0][j]-dataComb[i][1][j]

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