# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 00:19:49 2015

@author: Duncan

calculate various moments of correlation
"""

import numpy as np
import matplotlib.pyplot as plt
filename = "Set-3-DULETH13Cor"

# extract data into arrays

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt)
pps_T = [0]*len(contentsTxt)

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (',' in line):
		commaLoc = line.index(',')
		ser_T[j] = int(line[:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j+1]
pps_T = pps_T[:j+1]

ppsser_dT = [0]*len(ser_T)
for i in range(len(ppsser_dT)):
	ppsser_dT[i] = ser_T[i]-pps_T[i]
serser_dT = [0]*(len(ser_T)-1)
for i in range(len(serser_dT)):
	serser_dT[i] = ser_T[1+i]-ser_T[i]
ppspps_dT = [0]*(len(ser_T)-1)
for i in range(len(ppspps_dT)):
	ppspps_dT[i] = pps_T[1+i]-pps_T[i]
	
data = serser_dT
	
cor_x = range(0, 50)
cor_y = [0]*len(cor_x)
for order in cor_x:
	arr_1 = [0]*(len(data)-order)
	arr_2 = [0]*(len(data)-order)
	if (i>=0):
		for i in range(len(arr_1)):
			arr_1[i] = data[i]
			arr_2[i] = data[order+i]
	else:
		for i in range(len(arr_1)):
			arr_1[i] = data[order+i]
			arr_2[i] = data[i]
		
	cor_y[order] = np.corrcoef(arr_1, arr_2)[0][1]

plt.plot(cor_x, cor_y)
plt.scatter(cor_x, cor_y)
plt.title("ser-ser correlation coefficient")
plt.xlabel("order (time shift)")
plt.ylabel("value")
plt.xlim(min(cor_x), int(round(max(cor_x)/10.0)*10))
plt.show()
