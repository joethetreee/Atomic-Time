# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 12:15:23 2016

@author: Duncan

Analysis of initial GPS results
Plots time-domain graph of dt distribution
"""

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt

filename = "231312 18102015 GPSDrift_measurements"
binMin = 0
binMax = 2000
binWidth = 1
binNum = int((binMax-binMin)/binWidth)
binEdges = np.linspace(binMin,binMax,binNum+1)
binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]

contents = open("../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_dT = [0]*len(contentsTxt) 	# PPS times for data

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	char0 = line[0]
	if (char0>='0' and char0<='9'):
		for k in range(len(line)):
			chark = line[k]
			if (chark<'0' or chark>'9'):
				char0 = k
				break
		ser_dT[j] = int(line[0:char0])
		j += 1
			
ser_dT = ser_dT[:j]


binVals = np.histogram(ser_dT, bins=binEdges)[0]
binVals = [binVals[i]/(sum(binVals)*binWidth) for i in range(len(binVals))]

binFirst = binEdges[0]
for i in range(binNum):
	if (binVals[i]!=0):
		binFirst = binEdges[i]
		break
binLast = binEdges[-1]
for i in range(binNum):
	if (binVals[binNum-1-i]!=0):
		binLast = binEdges[binNum-1-i]
		break
	
print(binFirst, binLast)

mplt.rcParams.update({'font.size': 18})
fig = plt.figure(figsize=(10,6))

plt.plot(binMids,binVals,color="black")
plt.xlim(100*int(max(binMin, binFirst)/100), 100*int(min(binMax, binLast)/100+1))
plt.xlim(900,1100)
plt.title("Distribution of consecutive serial time differences")
plt.xlabel("Time difference /ms")
plt.ylabel("Probability density")
plt.savefig("../Plots/"+filename+"serser_dT_dist.png", dpi=400)
plt.savefig("../Plots/"+filename+"serser_dT_dist.svg")

mplt.rcParams.update({'font.size': 18})