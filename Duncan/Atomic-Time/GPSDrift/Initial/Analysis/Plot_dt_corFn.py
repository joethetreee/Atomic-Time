# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 00:19:49 2015

@author: Duncan

Analysis of initial GPS results
Plots time-domain graph of dt correlation
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


data = ser_dT
	
cor_x = range(0, 11)
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

mplt.rcParams.update({'font.size': 18})
fig = plt.figure(figsize=(10,6))

plt.plot(cor_x, cor_y, color="black")
plt.scatter(cor_x, cor_y, color="black", linewidth=0)
plt.plot(cor_x,[0]*len(cor_x), "k--")
plt.title("Serial-serial correlation function")
plt.xlabel("Order (sample difference)")
plt.ylabel("Correlation value")
plt.xlim(min(cor_x), int(round(max(cor_x)/10.0)*10))
plt.savefig("../Plots/"+filename+"serserCorFn.png", dpi=400)
plt.savefig("../Plots/"+filename+"serserCorFn.svg")

plt.show()