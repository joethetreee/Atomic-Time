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

filename = "KL1PRD00ChkCor"	

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
k1ek1e_dT = [dataCol[oset_est][i+1]-dataCol[oset_est][i] for i in range(len(dataRow)-1)]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

pltDat = [serser_dT  , ppspps_dT  , k1ek1e_dT  , ppsk1e_dT  , ppsser_dT]
savDat = ["serser_dT", "ppspps_dT", "k1ek1e_dT", "ppsk1e_dT", "ppsser_dT"]
titDat = ["Consecutive serial", "Consecutive PPS",
		"Consecutive single Kalman estimate", "PPS to single Kalman estimate", "PPS to serial"]

mplt.rcParams.update({'font.size': 14})
for i in range(len(pltDat)):
	
	data = pltDat[i]
	name = savDat[i]
	title = titDat[i]
	
	print(title, "min", min(data), data.index(min(data)), "max", max(data), data.index(max(data)))
	
	fig = plt.figure(figsize=(11,6))
	y_formatter = mplt.ticker.ScalarFormatter(useOffset=False)
	axes = plt.axes()
		
	plt.scatter(range(0,len(data),1),data, color="k", s=2, linewidth=0)
	plt.title(title+" time difference")
	plt.xlabel("Samples")
	plt.ylabel("Time difference /ms")
	plt.xlim(0,len(data))
	
	# find a measure of spread of data
	# find order of range
	dataRange = max(data)-min(data)
	order = 1
	while(order<dataRange):
		order*=10
	order/=10
	if (order>1):	order/=10
		
	plt.ylim(int(min(data)/order-1)*order, int(max(data)/order+1)*order)
	axes = plt.axes()
	axes.yaxis.set_major_formatter(y_formatter)
	
	plt.annotate("Average: "+str(round(np.average(data),2))+" ms;  Std dev: "+
			str(round(np.std(data),2))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
			
	saveFileName = filename+"_"+name+"("+str(start)+"-"+str(end)+")"
	plt.savefig("../../Results/"+saveFileName+".png", dpi=400)
	plt.savefig("../../Results/"+filename+"_"+name+"("+str(start)+"-"+str(end)+").svg")
	plt.clf()