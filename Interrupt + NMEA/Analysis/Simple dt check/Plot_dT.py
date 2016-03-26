# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 14:01:47 2015

@author: Duncan

plot differences in time
used to check data

input format:
...
t<ser_time>,<pps_time>
...

doesn't matter which other lines are present; information extracted from t<><> row

"""

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt

filename = "GPSMIL37ChckdCor"	

contents = open("../../results/" + filename + ".txt", mode='r')
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
		
		
start = 0
end = j
end = min(end, j)
ser_T = ser_T[start:end]
pps_T = pps_T[start:end]

# find quality types in data
	
ppsser_dT = [0]*len(ser_T)
for i in range(len(ppsser_dT)):
	ppsser_dT[i] = ser_T[i]-pps_T[i]
	
serser_dT = [0]*(len(ser_T)-1)
for i in range(len(serser_dT)):
	serser_dT[i] = ser_T[1+i]-ser_T[i]
	
ppspps_dT = [0]*(len(pps_T)-1)	
for i in range(len(ppspps_dT)):
	ppspps_dT[i] = pps_T[1+i]-pps_T[i]
	
print("ppsser_dT max, min, avg, std: "+str(max(ppsser_dT))+", "+str(min(ppsser_dT))+", "+str(np.average(ppsser_dT))+", "+str(np.std(ppsser_dT)))
print("serser_dT max, min, avg, std: "+str(max(serser_dT))+", "+str(min(serser_dT))+", "+str(np.average(serser_dT))+", "+str(np.std(serser_dT)))
print("ppspps_dT max, min, avg, std: "+str(max(ppspps_dT))+", "+str(min(ppspps_dT))+", "+str(np.average(ppspps_dT))+", "+str(np.std(ppspps_dT)))

y_formatter = mplt.ticker.ScalarFormatter(useOffset=False)
axes = plt.axes()
mplt.rcParams.update({'font.size': 12})

fig = plt.figure(figsize=(10,6))
plt.scatter(range(0,len(serser_dT),1),serser_dT, color="k", s=2, linewidth=0)
plt.title("Consecutive serial time difference")
plt.xlabel("Samples")
plt.ylabel("Time difference /ms")
plt.xlim(0,len(serser_dT))
axes = plt.axes()
axes.yaxis.set_major_formatter(y_formatter)
plt.savefig("../../Results/"+filename+"serser_dT("+str(start)+"-"+str(end)+").png", dpi=400)
plt.savefig("../../Results/"+filename+"serser_dT("+str(start)+"-"+str(end)+").svg")

fig = plt.figure(figsize=(10,6))
plt.scatter(range(0,len(ppsser_dT),1),ppsser_dT, color="k", s=2, linewidth=0)
plt.title("PPS-serial time difference")
plt.xlabel("Samples")
plt.ylabel("Time difference /ms")
plt.xlim(0,len(ppsser_dT))
plt.ylim(int(min(ppsser_dT)/20)*20, int(max(ppsser_dT)/20+1)*20)
#plt.ylim(0,1000)
axes = plt.axes()
axes.yaxis.set_major_formatter(y_formatter)
plt.savefig("../../Results/"+filename+"ppsser_dT("+str(start)+"-"+str(end)+").png", dpi=400)
plt.savefig("../../Results/"+filename+"ppsser_dT("+str(start)+"-"+str(end)+").svg")

fig = plt.figure(figsize=(10,6))
plt.scatter(range(0,len(ppspps_dT),1),ppspps_dT, color="k", s=2, linewidth=0)
plt.title("Consecutive PPS time difference")
plt.xlabel("Samples")
plt.ylabel("Time difference /ms")
plt.xlim(0,len(ppspps_dT))
y_formatter = mplt.ticker.ScalarFormatter(useOffset=False)
axes = plt.axes()
axes.yaxis.set_major_formatter(y_formatter)
plt.savefig("../../Results/"+filename+"ppspps_dT("+str(start)+"-"+str(end)+").png", dpi=400)
plt.savefig("../../Results/"+filename+"ppspps_dT("+str(start)+"-"+str(end)+").svg")
plt.show()