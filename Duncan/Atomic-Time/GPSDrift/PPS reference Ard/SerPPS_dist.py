# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 18:05:29 2015

@author: Duncan

Generate distribution of PPS-serial, but with lines rather than bars for less ink

format
--
<ser time>,<pps time>
--
"""
import numpy as np
import matplotlib.pyplot as plt

filename = "PPSSER12"

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt)
pps_T = [0]*len(contentsTxt)

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	commaLoc = line.index(',')
	ser_T[j] = int(line[0:commaLoc])
	pps_T[j] = int(line[commaLoc+1:])
	j += 1
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]

ppsser_dT = [ser_T[i]-pps_T[i] for i in range(len(ser_T))]

binMin = 0
binMax = 1000
binWidth = 4
binNum = (binMax-binMin)/binWidth
binEdges = np.linspace(binMin,binMax,binNum+1)
binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]

binVals = np.histogram(ppsser_dT, bins=binEdges)[0]
binVals = [binVals[i]/(sum(binVals)*binWidth) for i in range(len(binVals))]

plt.plot(binMids,binVals)
plt.title("Distribution of PPS-Serial times, data "+filename)
plt.xlabel("Time /ms")
plt.ylabel("Probability Density")