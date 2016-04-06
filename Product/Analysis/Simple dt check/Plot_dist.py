# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot differences in time
used to check data

input format:
...
<ser_time>,<pps_time>,<est_time>,...
...

doesn't matter which other lines are present; information extracted from t<><> row

"""
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt

filename = "KL1PRD09ChkCor"	

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
		dataRow[row][col] = float(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1

if (end=="end"):
	end = len(dataRow)
end = min(end, len(dataRow))
dataRow = dataRow[start:end]
		
dataCol = [[0]*len(dataRow) for i in range(parts)]

for row in range(len(dataRow)):
	for col in range(parts):
		dataCol[col][row] = dataRow[row][col]

# find quality types in data
	
serser_dT = [dataCol[oset_ser][i+1]-dataCol[oset_ser][i] for i in range(len(dataRow)-1)]
ppspps_dT = [dataCol[oset_pps][i+1]-dataCol[oset_pps][i] for i in range(len(dataRow)-1)]
k1ek1e_dT = [dataCol[oset_est][i+1]-dataCol[oset_est][i] for i in range(len(dataRow)-1)]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

pltDat = [serser_dT  , ppspps_dT  , k1ek1e_dT  , ppsk1e_dT  , ppsser_dT]
savDat = ["serser_dT", "ppspps_dT", "k1ek1e_dT", "ppsk1e_dT", "ppsser_dT"]
titDat = ["Consecutive serial", "Consecutive PPS",
		"Consecutive single Kalman estimate", "PPS to single Kalman estimate", "PPS to serial"]

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
	while(order>dataRange):
		order/=10
	while(order<dataRange):
		order*=10
	order = order/100
	order_i = int(round(np.log10(order)))
		
	spacing = 1
	if (order<1): spacing = order/50
	stdDev = np.std(data)
	j=0
	stdDev_ = round(stdDev,j)
	while(stdDev_==0 and stdDev>0.00001):
		stdDev_ = round(stdDev,j+1)
		j+=1
	if(j==0):	stdDev_ = int(stdDev_)
	
	(binVals, binMids) = GenerateDist(data, int(min(data)/order-1)*order, int(max(data)/order+1)*order, spacing)
	plt.plot(binMids, binVals, color = "black")
	plt.title("Distribution of "+title+" time differences")
	plt.xlabel("Time difference /ms")
	plt.ylabel("Probability density")
	plt.annotate("Average: "+str(round(np.average(data),1))+" ms;  Std dev: "+
			str(stdDev_)+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
	plt.savefig("../../Results/"+filename+"_"+name+"_dist.png", dpi=400)
	plt.savefig("../../Results/"+filename+"_"+name+"_dist.svg")
	plt.show()