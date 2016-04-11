# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 00:41:57 2016

@author: Duncan
"""

import numpy as np
import statsmodels.tsa.stattools as ts
import KalmanFilter as klm
import matplotlib.pyplot as plt

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

start = 0
end = "end"

average = False 					# whether to average the data (means we can test for long-term effects quicker)
averageNum = 20	 				# how many consecutive values to average

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
	
serser_dT = [dataCol[oset_ser][i+1]-dataCol[oset_ser][i] for i in range(len(dataRow)-1)]
ppspps_dT = [dataCol[oset_pps][i+1]-dataCol[oset_pps][i] for i in range(len(dataRow)-1)]
k1ek1e_dT = [dataCol[oset_est][i+1]-dataCol[oset_est][i] for i in range(len(dataRow)-1)]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

klm_T = [dataCol[oset_ser][0]]*len(dataCol[oset_ser])
klm_U = 1
est_dT = 999.983
est_U = 0.001
meas_U = 40
for i in range(len(klm_T)-1):
	klm_T[1+i],klm_U = klm.KalFilIter(klm_T[i], est_dT, dataCol[oset_ser][1+i], klm_U, est_U, meas_U)

ppsklm_dT = [klm_T[i]-dataCol[oset_pps][i] for i in range(len(klm_T))]
	
print(len(ppsklm_dT), 12*(len(ppsklm_dT)/100)**(1/4))

pltDat = [serser_dT  , ppspps_dT  , k1ek1e_dT  , ppsk1e_dT  , ppsser_dT, ppsklm_dT]
savDat = ["serser_dT", "ppspps_dT", "k1ek1e_dT", "ppsk1e_dT", "ppsser_dT", "ppsklm_dT"]
titDat = ["Consecutive serial", "Consecutive PPS",
		"Consecutive single Kalman estimate", "PPS to single Kalman estimate", "PPS to serial", "PPS to new Klm"]

#x=[0]*100
#for i in range(len(x)):
#	x[i] = i + (np.random.random()-0.5)*1
#print(ts.adfuller(x))
#
#x=[0]*100
#for i in range(len(x)):
#	x[i] = i + (np.random.random()-0.5)*len(x)
#print(ts.adfuller(x))
#
#x=[0]*100
#for i in range(len(x)):
#	x[i] = i + (np.random.random()-0.5)*len(x)*100
#print(ts.adfuller(x))

for i in range(len(pltDat)):
	
	data_ = pltDat[i]
	if (average):
		data = []
		num = int(len(data_)/averageNum)
		for j in range(num):
			tot = 0
			for k in range(averageNum):
				tot += data_[j*averageNum + k]
			tot /= averageNum
			data.append(tot)
	else:
		data = data_
	name = savDat[i]
	title = titDat[i]
	
	print(title, ts.adfuller(data))
	plt.scatter(range(len(data)),data, linewidth=0, color='k', s=2)
	plt.title(title)
	plt.show()
	
	freq = [j/len(data) for j in range(len(data))]
	data_f = np.fft.fft(data)
	
	plt.scatter(freq, np.log(data_f), linewidth=0, color='k', s=2)
	plt.show()