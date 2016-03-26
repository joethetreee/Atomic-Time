# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot based on number of satellites

data must contain the following two lines
$GPGGA
txxxx,xxxx 	    (serial,pps times)
"""
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
filename = "GPSMIL37ChckdCor"

oset_GGA = 0 				# offset of GGA sentence
oset_PPS = 2 				# offset of PPS sentence
period = 3	 				# number of lines in each data set
qCommaIndex = 7				# number of commas in GGA line before data

start = 0
end = 5000

def ColArray(N):
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

if (end=="end"):
	end = len(contentsTxt)/period
end = int(min(end, len(contentsTxt)/period))

print("length: ",end)
ser_T = [0]*end	 	# store serial times
pps_T = [0]*end	 	# store pps times
qArr = [0]*end	 	# store connections quality
print("~",end)

# put data into arrays

for i in range(0,end,1):
	# get information from GGA sentence
	commaLoc = 0
	line = contentsTxt[i*period+oset_GGA]
	for commaNum in range(qCommaIndex): 	 	 	# value of interest
		commaLoc += line[commaLoc:].index(',')+1
	commaLoc2 = commaLoc + line[commaLoc:].index(',')
	qArr[i] = int(float(line[commaLoc:commaLoc2]))
	
	# get information from PPS sentence
	commaLoc = 0
	line = contentsTxt[i*period+oset_PPS]
	for commaNum in range(1): 	 	 	 	 	# find pps value
		commaLoc += line[commaLoc:].index(',')
	ser_T[i] = int(line[1:commaLoc])
	pps_T[i] = int(line[commaLoc+1:])

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

x_data = np.linspace(0, len(ppsser_dT)/1000-1, len(ppsser_dT))

mplt.rcParams.update({'font.size': 15})
fig = plt.figure(figsize=(11,6))
	
s = plt.scatter(x_data, ppsser_dT, c=qArrN, cmap=plt.cm.gist_rainbow    ,    linewidth='0', s=2)
plt.xlim(min(x_data), max(x_data))
plt.ylim(max(0, int(min(ppsser_dT)/100)*100), min(1000, int(max(ppsser_dT)/100+1)*100))
cbarTicksTemp = np.linspace(min(qTypesN), max(qTypesN), len(qTypesN))
cbar = plt.colorbar(s, ticks=cbarTicksTemp)
cbarTicksNew = np.linspace(min(qTypes), max(qTypes), len(qTypes), dtype = int)
print (cbarTicksTemp)
print(cbarTicksNew)
cbar.ax.set_yticklabels(cbarTicksNew)  # horizontal colorbar
plt.title("PPS-serial difference with satellite number")
plt.ylabel("difference in time / ms")
plt.xlabel("Samples (thousands)")

print(pearsonr(ppsser_dT, qArr))

saveFileName = filename+"SerPPS_satNum"
plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
plt.savefig("../../Results/"+saveFileName+".svg")

plt.show()
