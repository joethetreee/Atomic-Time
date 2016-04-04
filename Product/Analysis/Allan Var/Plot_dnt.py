# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 22:07:12 2016

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

n = 10000
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

# find quality types in data
ppspps_dnT = [(dataCol[oset_pps][i+n]-dataCol[oset_pps][i])/n for i in range(0,len(dataCol[oset_pps])-n)]

fig = plt.figure(figsize=(10,6))
y_formatter = mplt.ticker.ScalarFormatter(useOffset=False)
axes = plt.axes()
mplt.rcParams.update({'font.size': 12})

plt.scatter(range(0,len(ppspps_dnT),1),ppspps_dnT, color="k", s=2, linewidth=0)
plt.title("Moving average PPS time difference order "+str(n))
plt.xlabel("Samples")
plt.ylabel("Time difference /ms")
plt.xlim(0,len(ppspps_dnT))
y_formatter = mplt.ticker.ScalarFormatter(useOffset=False)
axes = plt.axes()
axes.yaxis.set_major_formatter(y_formatter)
plt.savefig("../../Results/"+filename+"_ppspps_dnT_"+str(n)+"("+str(start)+"-"+str(end)+").png", dpi=400)
plt.savefig("../../Results/"+filename+"_ppspps_dnT_"+str(n)+"("+str(start)+"-"+str(end)+").svg")

plt.show()