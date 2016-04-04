# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot differences in time
used to check data

input format:
...
<ser_time>,<pps_time>
...

doesn't matter which other lines are present; information extracted from t<><> row

"""
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt

filename = "INTPRD01ChkCor"	

contents = open("../../results/" + filename + ".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

print("length: ",len(contentsTxt))
ser_T = [0]*len(contentsTxt)	 	# store serial times
pps_T = [0]*len(contentsTxt)	 	# store pps times
parts = 2
dataRow = [[0]*parts for i in range(len(contentsTxt))]
oset_ser = 0
oset_pps = 1
binWidth = 1

start = 0
end = "end"

# put data into arrays
for row in range(len(dataRow)):
	line = contentsTxt[row]
	commaLoc,commaLoc2 = 0,0
	for col in range(parts):
		if (col==parts-1):
			commaLoc2 = len(line)
		else:
			commaLoc2 = commaLoc+line[commaLoc:].index(',')
		dataRow[row][col] = int(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1
		
dataCol = [[0]*len(dataRow) for i in range(parts)]

for row in range(len(dataRow)):
	for col in range(parts):
		dataCol[col][row] = dataRow[row][col]

if (end=="end"):
	end = len(dataRow)
end = min(end, len(dataRow))
dataRow = dataRow[start:end]

# find quality types in data
	
serser_dT = [dataCol[oset_ser][i+1]-dataCol[oset_ser][i] for i in range(len(dataRow)-1)]
ppspps_dT = [dataCol[oset_pps][i+1]-dataCol[oset_pps][i] for i in range(len(dataRow)-1)]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

pltDat = [serser_dT  , ppspps_dT  , ppsser_dT]
savDat = ["serser_dT", "ppspps_dT", "ppsser_dT"]
titDat = ["Consecutive serial", "Consecutive PPS", "PPS to serial"]

def GenerateDist(histData_, binMin_, binMax_, binWidth_):
	binWidth_ = int(round(binWidth_))
	binNum_ = (binMax_-binMin_)/binWidth_
	if (binNum_!=int(binNum_)):
		binMax_ += (binWidth_-(binMax_-binMin_)%binWidth_)%binWidth
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
	
mplt.rcParams.update({'font.size': 14})
for i in range(len(pltDat)):
	
	data = pltDat[i]
	name = savDat[i]
	title = titDat[i]

	fig = plt.figure(figsize=(11,6))
	
	# find a measure of spread of data
	# find order of range
	dataRange = max(data)-min(data)
	order = 1
	while(order<dataRange):
		order*=10
	order = max(10,order/10)
	if (order>1):	order/=10
		
	(binVals, binMids) = GenerateDist(data, int(min(data)/order-1)*order, int(max(data)/order+1)*order, binWidth)
	plt.plot(binMids, binVals, color = "black")
	plt.title("Distribution of "+title+" time differences")
	plt.xlabel("Time difference /ms")
	plt.ylabel("Probability density")
	plt.annotate("Average: "+str(round(np.average(data),1))+" ms;  Std dev: "+
			str(int(round(np.std(data),0)))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
	plt.savefig("../../Results/"+filename+"_"+name+"_dist.png", dpi=400)
	plt.savefig("../../Results/"+filename+"_"+name+"_dist.svg")
	plt.show()