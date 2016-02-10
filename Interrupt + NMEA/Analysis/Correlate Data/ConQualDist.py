# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot based on number of satellites
"""

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
filename = "GPSMIL12ChckdCor"
normalise = False

oset_GGA = 0 				# offset of GGA sentence
oset_PPS = 1 				# offset of PPS sentence
period = 2 				# number of lines in each data set
qCommaIndex = 7				# number of commas in GGA line before data


def ColArray(N):
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours
	

def Median(data):
	tot = sum(data)
	tot_=0
	for i in range(len(data)):
		tot_ += data[i]
		if (tot_>=tot/2):
			return i
	

contents = open("../../Results/"+filename+".txt", mode='r')
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
	
qTypesN = [0]*len(qTypes) 							# quality types normalised up to 1.0
qTypesNZ = [0]*len(qTypes) 						# quality types normalised between 0.0->1.0
qArrN = [0]*len(qArr)
qArrNZ = [0]*len(qArr)
qMax = max(qTypes)
qMin = min(qTypes)
for i in range(len(qTypes)):
	qTypesN[i] = qTypes[i]/qMax
	qTypesNZ[i] = (qTypes[i]-qMin)/(qMax-qMin)
for i in range(len(qArrN)):
	qArrN[i] = qArr[i]/qMax
	qArrNZ[i] = (qArr[i]-qMin)/(qMax-qMin)
	
ppsser_dT_ = [[] for i in range(len(dataComb))]
for i in range(len(ppsser_dT_)):
	ppsser_dT_[i] = [0]*len(dataComb[i][0])
	for j in range(len(ppsser_dT_[i])):
		ppsser_dT_[i][j] = dataComb[i][0][j]-dataComb[i][1][j]

binMin = 0
binMax = 1000
binNum = 1000
ser_leg = [0]*len(ppsser_dT_)
txt_leg = [str(i) for i in qTypes]

# plot a scatter plot so we can get our colours for the colour bar (can't do with plt.plot); discard
cbarPlot = plt.scatter(range(0,len(ppsser_dT),1),ppsser_dT,c=qArrNZ, cmap=plt.cm.gist_rainbow,linewidth='0', s=8)
plt.clf()
fig = plt.figure(figsize=(11,6))
mplt.rcParams.update({'font.size': 15})

medianArr = [0]*len(ppsser_dT_)
for j in range(len(ppsser_dT_)):
	histData = ppsser_dT_[j]
	binWidth = (binMax - binMin)/binNum
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
		
	print(qTypes[j])
		
	ser_leg[j] ,= plt.plot(binMids, binVals, color=plt.cm.gist_rainbow(qTypesNZ[j]))
	medianArr[j] = binMids[Median(binVals)]
print(pearsonr(medianArr, qTypes))
	
	
plt.title("Dist. of PPS-serial difference by satellite number")
plt.xlabel("Time difference /ms")
plt.ylabel("Frequency")

cbarTicksTemp = np.linspace(min(qTypesNZ), max(qTypesNZ), len(qTypesNZ))
cbar = plt.colorbar(cbarPlot, ticks=cbarTicksTemp)
cbarTicksNew = np.linspace(min(qTypes), max(qTypes), len(qTypes), dtype = int)
print (cbarTicksTemp)
print(cbarTicksNew)
cbar.ax.set_yticklabels(cbarTicksNew)  # horizontal colorbar

saveFileName = filename+"SerPPS_satNum_dist"
plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
plt.savefig("../../Results/"+saveFileName+".svg")

plt.show()

print(pearsonr(ppsser_dT, qArr))