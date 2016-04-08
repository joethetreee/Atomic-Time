# -*- coding: utf-8 -*-
"""
Created on Wed Apr 6 23:12:57 2016

@author: Duncan
"""

import numpy as np
import statsmodels.tsa.stattools as ts
import KalmanFilter as klm
import matplotlib.pyplot as plt
import matplotlib as mplt

filename = "KL1PRD10ChkCor"	

contents = open("../../results/" + filename + ".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

print("length: ",len(contentsTxt))
ser_T = [0]*len(contentsTxt)	 	# store serial times
pps_T = [0]*len(contentsTxt)	 	# store pps times
parts = 4
dataRow = [[0]*parts for i in range(len(contentsTxt))]
oset_ser = 0
oset_pps = 1
oset_est = 2
oset_sat = 3


satOffsets = [184, 194, 201, 214, 226, 235, 243, 252, 273, 299, 302, 303]
satUncerts = [23 , 20 , 15 , 12 , 12 , 13 , 13 , 16 , 21 , 23 , 25 , 20 ]

start = 0
end = "end"

def GetSatOffset(satNum):
	satNum = int(satNum)
	if (satNum < len(satOffsets)):
		return (satOffsets[satNum], satUncerts[satNum])
	else:
		print("!!Return last")
		return (satOffsets[-1], satUncerts[-1])

# put data into arrays
for row in range(len(dataRow)):
	line = contentsTxt[row]
	commaLoc,commaLoc2 = 0,0
	for col in range(parts):
		if (col==parts-1):
			commaLoc2 = len(line)
		else:
			commaLoc2 = commaLoc+line[commaLoc:].index(',')
		try:	dataRow[row][col] = int(line[commaLoc:commaLoc2])
		except ValueError:	dataRow[row][col] = float(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1

if (end=="end"):
	end = len(dataRow)
end = min(end, len(dataRow))
dataRow = dataRow[start:end]

		
dataCol = [[0]*len(dataRow) for i in range(parts)]

for row in range(len(dataRow)):
	for col in range(parts):
		dataCol[col][row] = dataRow[row][col]

# split data into segments, use Teensy clock entirely for these (sec grid) and find average difference filter - sec
# use this difference to adjust the grid size
seg_T = [dataCol[oset_ser][0]-GetSatOffset(dataCol[oset_sat][0])[0]]*len(dataCol[oset_ser])	# Kalman filter segmented
est_dT = 999.983			# default second length
est_U = 0.0001			# default second length uncertainty
segSize = 5000			# uses Teensy clock to generate this many prediction times, then estimate uncertainties

sec_t = est_dT 			# second length used in segmenting algorithm
sec_u = est_U 			# second length uncertainty used in segmenting algorithm
bias_t = 0 				# bias for segment used in segmenting algorithm
bias_u = 20				# uncertainty in bias for segment used in segmenting algorithm (unused in the current state)

### SEGMENTING ALGORITHM ###

for seg in range(int(len(seg_T)/segSize)):
	# set each estimation in new segment to a second length apart starting from initial predicted value minus bias
	for i in range(segSize):
		# (1-exp) factor is to phase in the new bias, reducing jumps in second length
		seg_T[segSize*seg + i] = seg_T[segSize*seg] + i*est_dT - bias_t*(1-np.exp(-5*i/segSize))
	# if we are going to have another segment after this, we set the initial value here
	if (len(seg_T)>=segSize*(seg+1)):
		seg_T[segSize*(seg+1)] = seg_T[segSize*seg] + segSize*est_dT - bias_t
	# measure bias
	biasE_t = 0						# Expected bias (this used to be passed through Kalman filter)
	weightTot = 0						# how much weight the bias has
	for i in range(segSize):
		j = segSize*seg + i
		weight = sec_u*(i**0.2)		# weight of individual point -- more important towards end of segment
		weightTot += weight
		biasE_t += ( seg_T[j] - (dataCol[oset_ser][j]-GetSatOffset(dataCol[oset_sat][j])[0]) )*weight
	biasE_t /= weightTot
	if (len(seg_T)>=segSize*(seg+1)):
		bias_t = biasE_t				# we have no Kalman filter for bias now, so we just set the bias to expected bias
		
# cut array of data to the end of the last segment
seg_T = seg_T[:int(len(seg_T)/segSize)*segSize]
	
	
ppsseg_dT = [seg_T[i]-dataCol[oset_pps][i] for i in range(len(seg_T))]
		
pltDat = [ppsseg_dT]
savDat = ["ppsseg_T"]
titDat = ["PPS to segmented KalEst"]


mplt.rcParams.update({'font.size': 14})
for i in range(len(pltDat)):
	fig = plt.figure(figsize=(11,6))
	
	data = pltDat[i]
	name = savDat[i]
	title = titDat[i]
	
	cor = ts.acf(data, nlags=len(data))
	
	#plt.plot(range(len(cor)), cor)
	plt.scatter(range(len(data)), data, linewidth=0, s=1, c='k')
	plt.title(title + " time difference")
	plt.xlabel("Sample")
	plt.ylabel("Time difference / ms")
	plt.xlim(0, len(data))
	plt.ylim(int(min(data)/10-1)*10, int(max(data)/10+1)*10)
	
	plt.annotate("Average: "+str(round(np.average(data),2))+" ms;  Std dev: "+
			str(round(np.std(data),2))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
	plt.tight_layout()
	
	#plt.savefig("../../Results/"+filename+"_"+name+"_filter.png", dpi=400)
	plt.show()
	

contents = open("../../Results/"+filename[:8]+"Seg"+".txt", mode='w')		# open/create file to write

for i in range(len(seg_T)):
	contents.write(str(dataCol[oset_pps][i]))
	contents.write(",")
	contents.write(str(seg_T[i]))
	contents.write(",")
	contents.write(str(dataCol[oset_sat][i]))
	contents.write("\n")
	
contents.close()