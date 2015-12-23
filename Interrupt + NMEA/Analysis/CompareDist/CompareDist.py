# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 13:21:11 2015

@author: Duncan

Estimate PPS time for working data using a reference PPS-Serial distribution

Calculate average ser-ser time (which should be second length)
Find offset to get to PPS time by doing convolution/correlation of distributions
"""

import numpy as np
import matplotlib.pyplot as plt
import KalmanFilter as klm

filenameC = "GPSMIL33ChckdCor" 	# cast filename
filename = "GPSMIL33ChckdCor" 	# filename of data do be cast
binMin = -1000
binMax = 1000
binWidth = 2
binNum = (binMax-binMin)/binWidth
binEdges = np.linspace(binMin,binMax,binNum+1)
binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]

# extract data into arrays

contentsC = open(filenameC+".txt", mode='r')
contentsTxtC = contentsC.readlines()
contentsC.close()

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt) 	# PPS times for data
pps_T = [0]*len(contentsTxt) 	# serial times for data

ser_TC = [0]*len(contentsTxtC) 	# PPS times for cast
pps_TC = [0]*len(contentsTxtC) 	# serial times for cast

j = 0
for i in range(len(contentsTxtC)):
	line = contentsTxtC[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_TC[j] = int(line[1:commaLoc])
		pps_TC[j] = int(line[commaLoc+1:])
		j += 1
		
ser_TC = ser_TC[:j]
pps_TC = pps_TC[:j]
ppsser_dTC = [ser_TC[i]-pps_TC[i] for i in range(len(pps_TC))]

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]
#ser_T = ser_T[30000:40000]
#pps_T = pps_T[30000:40000]

# get second length and find secser_dT
avgTx = 1000 							# expected length of second
avgTu = 1 							# uncertainty in length of second
secser_dT = [0]*len(ser_T)
sampleSize = 2000
sampleNum = int(len(secser_dT)/sampleSize)
ser_T = ser_T[:sampleSize*sampleNum]
pps_T = pps_T[:sampleSize*sampleNum]
tOff = 0 							# number of milliseconds to remove
for i in range(sampleNum):
	sample_pps_T = pps_T[i*sampleSize:(i+1)*sampleSize]
	sample_ser_T = ser_T[i*sampleSize:(i+1)*sampleSize]
	sample_serser_dT = [sample_ser_T[1+i]-sample_ser_T[i] for i in range(len(sample_ser_T)-1)]
	avgTu_ = np.std(sample_serser_dT)*2/sampleSize
	avgTx_ = (sample_ser_T[-1]-sample_ser_T[0])/(len(sample_ser_T)-1)
	#avgTx_ = (sample_pps_T[-1]-sample_pps_T[0])/(len(sample_pps_T)-1)
	avgTu_=0
	(avgTx,avgTu) = klm.KalFilIter(avgTx,0,avgTx_,avgTu,1,avgTu_,1,1,1)
	for j in range(sampleSize):
		secser_dT[i*sampleSize+j] = sample_ser_T[j]-(ser_T[0]+tOff)
		tOff += avgTx
	print("avgtx,avgTu",avgTx,avgTu,avgTu_)


# get template distribution

binValsC = np.histogram(ppsser_dTC, bins=binEdges)[0]
binVals = np.histogram(secser_dT, bins=binEdges)[0]
binValsC = [binValsC[i]/(sum(binValsC)*binWidth) for i in range(len(binValsC))]
binVals = [binVals[i]/(sum(binVals)*binWidth) for i in range(len(binVals))]


plt.figure()
plt.plot(binMids, binValsC)
plt.plot(binMids, binVals)
plt.show()

# make sure we have peak at centre of binVals (might have some values out of bin range otherwise)
dOffsetTot = 0
#while (True):
#    iPeak = binMids[np.argmax(binVals)]
#    print(iPeak)
#    if (abs(iPeak-500)<=(binWidth*2)):
#        break
#    dOffset = iPeak-500
#    dOffsetTot += dOffset
#    print("dOT",dOffsetTot)
#    secser_dT = [secser_dT[i]-dOffset for i in range(len(secser_dT))]
#    binVals = np.histogram(secser_dT, bins=binEdges)[0]
binVals = [binVals[i]/(sum(binVals)*binWidth) for i in range(len(binVals))]
 
# find offset for secser_dT
oxBest=-1000            # optimal time offset
oyBest=0                # optimal "convolution" result

oxMin = -1000
oxMax = 1000
dox = binWidth*4

while(True):
    for ox in range(oxMin,oxMax,dox):
        ox_ = int(round(ox/binWidth,0))      # convert offset to the histogram spacing
        oy = 0
        for i in range(len(binVals)):
            if (i+ox_>=0 and i+ox_<len(binVals)):
                oy += binValsC[i]*binVals[i+ox_]
        if (oy>oyBest):
            oxBest = ox
            oyBest = oy
    print("best",oxBest)
    if (dox<=binWidth):
        break
    dox = int(dox/2)

oxBest_ = int(round(oxBest/binWidth,0))     # convert offset to the histogram spacing
for i in range(len(binVals)):
    if (i+oxBest_<0 or i+oxBest_>=len(binVals)):
        binVals[i] = 0
    else:
        binVals[i] = binVals[i+oxBest_]

# estimate pps times
print(oxBest, dOffsetTot)
ppsP_T = [ser_T[i]-(secser_dT[i]-oxBest) for i in range(len(ser_T))]
ppsser_dT = [ser_T[i]-pps_T[i] for i in range(len(pps_T))]
ppsppsP_dT = [ppsP_T[i]-pps_T[i] for i in range(len(pps_T))]

ppsppsPF_dT = [0]*len(ppsppsP_dT)
ppsppsPF_U = [0]*len(ppsppsP_dT)

ppsppsPF_dT[0] = ppsppsP_dT[0]
ppsppsPF_U[0] = 1
for i in range(1,len(ppsppsPF_U)):
	(ppsppsPF_dT[i],ppsppsPF_U[i]) = klm.KalFilIter(ppsppsPF_dT[i-1],0,(ppsppsP_dT[i]),
									ppsppsPF_U[i-1],0.00001,1, 1,1,1)

plt.figure()
#plt.plot(binMids, binValsC)
#plt.plot(binMids, binVals)
#ser_ppsser, = plt.plot(ppsser_dT)
ser_ppsppsP, = plt.plot(ppsppsP_dT)
#ser_ppsppsPF, = plt.plot(ppsppsPF_dT)
plt.xlabel("Samples")
plt.ylabel("PPS prediction accuracy /ms")
plt.title("PPS prediction using distribution profile")
#plt.legend([ser_ppsppsP, ser_ppsppsPF], ["pps-pred", "pps-pred Filtered"])
plt.annotate("Cast "+filenameC+"; data "+filename+" 30k-40k"+
	"; second len Ser end dif", xy=(0.05, 0.95), xycoords='axes fraction')
plt.show()