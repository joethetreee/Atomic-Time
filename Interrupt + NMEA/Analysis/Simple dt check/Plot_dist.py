# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 16:41:38 2016

@author: Duncan

Plot distributions
"""

# -*- coding: utf-8 -*-

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
filename = "GPSMIL12ChckdCor"
normalise = False

oset_GGA = 0 				# offset of GGA sentence
oset_PPS = 2 				# offset of PPS sentence
period = 3	 				# number of lines in each data set
qCommaIndex = 7				# number of commas in GGA line before data

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

print("length: ",len(contentsTxt))
ser_T = [0]*len(contentsTxt)	 	# store serial times
pps_T = [0]*len(contentsTxt)	 	# store pps times

# put data into arrays
j=0
for i in range(len(ser_T)):
	line = contentsTxt[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]

serser_dT = [ser_T[1+i]-ser_T[i] for i in range(len(ser_T)-1)]
ppspps_dT = [pps_T[1+i]-pps_T[i] for i in range(len(pps_T)-1)]
ppsser_dT = [ser_T[i]-pps_T[i] for i in range(len(ser_T))]

def GenerateDist(histData_, binMin_, binMax_, binWidth_):
	binNum_ = (binMax_-binMin_)/binWidth_
	binEdges_ = np.linspace(binMin_, binMax_, binNum_)
	binVals_ = np.histogram(histData_, bins=binEdges_)[0]
	
	tot_ = sum(binVals_)
	binVals2_ = [0.]*len(binVals_)
	for k in range(len(binVals_)):
		binVals2_[k] = float(binVals_[k])/tot_	
	
	binMids_ = [0]*len(binVals_)
	for i in range(len(binMids_)):
		binMids_[i] = (binEdges_[i]+binEdges_[1+i])/2.0
		
	return (binVals2_, binMids_)
	
mplt.rcParams.update({'font.size': 12})

fig = plt.figure(figsize=(10,6))
(binVals, binMids) = GenerateDist(serser_dT, 850, 1150, 1)
plt.plot(binMids, binVals, color = "black")
plt.title("Distribution of consecutive serial time differences")
plt.xlabel("Time difference /ms")
plt.ylabel("Probability density")
plt.savefig("../../Results/"+filename+"serser_dT_dist.png", dpi=400)
plt.savefig("../../Results/"+filename+"serser_dT_dist.svg")
plt.show()

fig = plt.figure(figsize=(10,6))
(binVals, binMids) = GenerateDist(ppsser_dT, 0, 1000, 4)
plt.plot(binMids, binVals, color = "black")
plt.title("Distribution of PPS-serial time differences")
plt.xlabel("Time difference /ms")
plt.ylabel("Probability density")
plt.savefig("../../Results/"+filename+"ppsser_dT_dist.png", dpi=400)
plt.savefig("../../Results/"+filename+"ppsser_dT_dist.svg")
plt.show()

fig = plt.figure(figsize=(10,6))
(binVals, binMids) = GenerateDist(ppspps_dT, 990, 1010, 1)
plt.plot(binMids, binVals, color = "black")
plt.title("Distribution time between consecutive serial messages")
plt.xlabel("Time difference /ms")
plt.ylabel("Probability density")
plt.savefig("../../Results/"+filename+"ppspps_dT_dist.png", dpi=400)
plt.savefig("../../Results/"+filename+"ppspps_dT_dist.svg")