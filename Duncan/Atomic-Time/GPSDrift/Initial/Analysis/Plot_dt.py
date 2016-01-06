# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 12:15:23 2016

@author: Duncan

Analysis of initial GPS results
Plots time-domain graph of dt
"""

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt

filename = "231312 18102015 GPSDrift_measurements"

contents = open("../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_dT = [0]*len(contentsTxt) 	# PPS times for data

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	char0 = line[0]
	if (char0>='0' and char0<='9'):
		for k in range(len(line)):
			chark = line[k]
			if (chark<'0' or chark>'9'):
				char0 = k
				break
		ser_dT[j] = int(line[0:char0])
		j += 1
			
ser_dT = ser_dT[:j]

mplt.rcParams.update({'font.size': 18})
fig = plt.figure(figsize=(10,6))

plt.scatter(range(0,len(ser_dT),1),ser_dT, s=2, linewidth = 0, c='black')
plt.xlim(0,len(ser_dT))
plt.title("Consecutive serial time difference")
plt.xlabel("Sample")
plt.ylabel("Time difference /ms")
plt.annotate("avg "+str(round(np.average(ser_dT),2))+" ms;  std dev "+str(round(np.std(ser_dT),2))+" ms",
													xy=(0.05, 0.95), xycoords='axes fraction')
plt.savefig("../Plots/"+filename+"serser_dT.png", dpi=400)
plt.savefig("../Plots/"+filename+"serser_dT.svg")

plt.show()