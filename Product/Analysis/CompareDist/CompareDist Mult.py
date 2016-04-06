# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 13:21:11 2015

@author: Duncan

Estimate PPS time for working data using a reference PPS-Serial distribution

Segment data; for each segment
Calculate average ser-ser time (which should be second length)
Find offset to get to PPS time by doing convolution/correlation of distributions

then use Kalman filter on each segment
"""

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import KalmanFilter as klm


def GetOffsetDist(dataThis, dataCast):
	""" Find offset in distributions between dataThis and dataCast
	returns offset defined such that dataThis[x->x+offset] gives best fit to dataCast[x]
	"""
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
	    if (dox<=binWidth):
	        break
	    dox = int(dox/2)
	return oxBest




filenameC = "GPSMIL33ChckdCor" 	# cast filename
filename = "GPSMIL33ChckdCor" 	# filename of data do be cast
binMin = -1000
binMax = 1000
binWidth = 6
binNum = (binMax-binMin)/binWidth
binEdges = np.linspace(binMin,binMax,binNum+1)
binMids = [int((binEdges[i+1]+binEdges[i])/2) for i in range(len(binEdges)-1)]

timing_PPS = False
segLen = 1000 				# number of seconds in segments


# extract data into arrays

contentsC = open("../../Results/"+filenameC+".txt", mode='r')
contentsTxtC = contentsC.readlines()
contentsC.close()

contents = open("../../Results/"+filename+".txt", mode='r')
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
		
start = 0
end = 10000
end = min(j,end)
ser_T = ser_T[start:end]
pps_T = pps_T[start:end]
#ser_T = ser_T[30000:40000]
#pps_T = pps_T[30000:40000]

# get template distribution

binValsC = np.histogram(ppsser_dTC, bins=binEdges)[0]
binValsC = [binValsC[i]/(sum(binValsC)*binWidth) for i in range(len(binValsC))]

# segment data and find secser (time difference between second grid and serial data)
segNum = int(len(ser_T)/segLen)
ppsP_T = [0]*(segNum*segLen)
ser_T = ser_T[:segNum*segLen]
pps_T = pps_T[:segNum*segLen]

udist = 20 			# uncertainty in distribution
oxf = 0 				# stores latest filtered offset value
ouf = udist*10		# stores latest uncertainty in offset value
secserPrev = 0
secLenFx = 1000.0
secLenFu = 2.0
SecLenU_p = 1
SecLenU_s = 100
dtTot = 0

for iSeg in range(segNum):
	# get segment data and find second lengths
	ppsData = pps_T[iSeg*segLen:(iSeg+1)*segLen]
	serData = ser_T[iSeg*segLen:(iSeg+1)*segLen]
	serser_dData = [serData[1+i]-serData[i] for i in range(len(serData)-1)]
	if (timing_PPS==True):
		secLenx_ = (ppsData[-1]-ppsData[0])/(len(ppsData)-1)
		secLenU_ = SecLenU_p/np.sqrt(len(ppsData))
	else:
		secLenx_ = (serData[-1]-serData[0])/(len(serData)-1)
		secLenU_ = np.std(serser_dData)*2/segLen
	if (i==0): secLenFu = secLenU_	
	
	(secLenFx,secLenFu) = klm.KalFilIter(secLenFx,0,secLenx_, secLenFu,1,secLenU_ ,1,1,1)
	
	# find secser and then find offset
	secser_dT = [serData[i]-serData[0]-i*secLenFx for i in range(len(serData))]
	binVals = np.histogram(secser_dT, bins=binEdges)[0]
	binVals = [binVals[i]/(sum(binVals)*binWidth) for i in range(len(binVals))]

#	plt.plot(binMids, binVals)
#	plt.plot(binMids, binValsC)
#	plt.show()

#	if (iSeg>0):
#		secserPrev = serData[0]-ser_T[(iSeg-1)*segLen]-dtTot 	# the "offset" of start of ith seg relative to 0th seg
#	dtTot = secLenFx*segLen
#	
	offset = GetOffsetDist(binVals,binValsC)
#	
#	(oxf,ouf) = klm.KalFilIter(oxf,0,offset+secserPrev, ouf,ouf,udist ,1,1,1)
#	
#	print(iSeg, " offset ", offset, oxf, secserPrev)
#	for j in range(segLen):
#		ppsP_T[iSeg*segLen+j] = ser_T[iSeg*segLen+j]-secser_dT[j]+oxf-secserPrev
	offset = GetOffsetDist(binVals,binValsC)
	print(iSeg, " offset ", offset, secserPrev)
	
	for j in range(segLen):
		ppsP_T[iSeg*segLen+j] = ser_T[iSeg*segLen+j]-secser_dT[j]+offset
	
ppsP_T = ppsP_T[:segNum*segLen]

# estimate pps times
ppsser_dT = [ser_T[i]-pps_T[i] for i in range(len(pps_T))]
ppsppsP_dT = [ppsP_T[i]-pps_T[i] for i in range(len(pps_T))]

ppsppsPF_dT = [0]*len(ppsppsP_dT)
ppsppsPF_U = [0]*len(ppsppsP_dT)

ppsppsPF_dT[0] = ppsppsP_dT[0]
ppsppsPF_U[0] = 1
for i in range(1,len(ppsppsPF_U)):
	(ppsppsPF_dT[i],ppsppsPF_U[i]) = klm.KalFilIter(ppsppsPF_dT[i-1],0,(ppsppsP_dT[i]),
									ppsppsPF_U[i-1],0.00001,1, 1,1,1)

mplt.rcParams.update({'font.size': 18})
fig = plt.figure(figsize=(10,6))
#plt.plot(binMids, binValsC)
#plt.plot(binMids, binVals)
#ser_ppsser, = plt.plot(ppsser_dT)
ser_ppsppsP, = plt.plot(ppsppsP_dT)
#ser_ppsppsPF, = plt.plot(ppsppsPF_dT)
plt.xlabel("Samples")
plt.ylabel("PPS prediction accuracy /ms")
plt.title("PPS prediction using distribution profile (segmented)")
#plt.legend([ser_ppsppsP, ser_ppsppsPF], ["pps-pred", "pps-pred Filtered"])
plt.annotate("(Segmented) Avg: "+str(round(np.average(ppsppsP_dT),1))+" ms;  std dev: "+
			str(round(np.std(ppsppsP_dT),1))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
saveFileName = filename+"("+str(start)+"-"+str(end)+")"+"CompDist"+filenameC+"_seg_serTime="+str(not timing_PPS)
plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
plt.savefig("../../Results/"+saveFileName+".svg")

plt.show()