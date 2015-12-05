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
import matplotlib.pyplot as plt

filename = "GPSMIL14ChckdCor"

def ColArray(N): 							# does colours
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours
	

contents = open(filename+".txt", mode='r')
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
		print(i, line)
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]

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

plt.plot(ppsser_dT)
plt.show()