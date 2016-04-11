# -*- coding: utf-8 -*-
"""
Created on Sun Apr 4 23:41:57 2016

@author: Duncan
"""

import numpy as np
import statsmodels.tsa.stattools as ts
import KalmanFilter as klm
import matplotlib.pyplot as plt
import matplotlib as mplt
mplt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
mplt.rc('text', usetex=True)

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
oset_sat = 3


satOffsets = [185, 193, 205, 215, 227, 235, 245, 255, 275, 294, 302, 303]
satUncerts = [25 , 20 , 20 , 12 , 13 , 13 , 15 , 20 , 21 , 25 , 22 , 20 ]

start = 0
end = "end"

def GetSatOffset(satNum):
	satNum = int(satNum)
	if (satNum < len(satOffsets)):
		return (satOffsets[satNum], satUncerts[satNum])
	else:
		print("!!Return last")
		return (satOffsets[-1], satUncerts[-1])

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
	
serser_dT = [dataCol[oset_ser][i+1]-dataCol[oset_ser][i] for i in range(len(dataRow)-1)]
ppspps_dT = [dataCol[oset_pps][i+1]-dataCol[oset_pps][i] for i in range(len(dataRow)-1)]
k1ek1e_dT = [dataCol[oset_est][i+1]-dataCol[oset_est][i] for i in range(len(dataRow)-1)]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

#klm_T = [dataCol[oset_ser][0]]*len(dataCol[oset_ser])
#klm_U = 100
#est_dT = 999.983
#est_U = 0.001
#meas_U = 20
#for i in range(len(klm_T)-1):
#	klm_T[1+i],klm_U = klm.KalFilIter(klm_T[i], est_dT, dataCol[oset_ser][1+i], klm_U, est_U, meas_U)
#ppsklm_dT = [klm_T[i]-dataCol[oset_pps][i] for i in range(len(klm_T))]
#
#k2e_T = [dataCol[oset_ser][0]-GetSatOffset(dataCol[oset_sat][0])[0]]*len(dataCol[oset_ser])
#k2e_U = 100
#est_dT = 999.983
#est_U = 0.001
#for i in range(len(k2e_T)-1):
#	satOset, satUncert = GetSatOffset(dataCol[oset_sat][1+i])
#	k2e_T[1+i],k2e_U = klm.KalFilIter(k2e_T[i], est_dT, dataCol[oset_ser][1+i]-satOset,
#										k2e_U, est_U, satUncert)
#ppsk2e_dT = [k2e_T[i]-dataCol[oset_pps][i] for i in range(len(k2e_T))]
#
#	
#plt.scatter(range(len(ppsklm_dT)),ppsklm_dT, linewidth=0, color='k', s=2)
#print(np.average(ppsklm_dT), np.std(ppsklm_dT))
#plt.show()
#plt.scatter(range(len(ppsk1e_dT)),ppsk1e_dT, linewidth=0, color='k', s=2)
#print(np.average(ppsk1e_dT), np.std(ppsk1e_dT))
#plt.show()
#plt.scatter(range(len(ppsk2e_dT)),ppsk2e_dT, linewidth=0, color='k', s=2)
#print(np.average(ppsk2e_dT), np.std(ppsk2e_dT))
#plt.show()

#pltDat = [serser_dT  , ppspps_dT  , k1ek1e_dT  , ppsk1e_dT  , ppsser_dT, ppsklm_dT]
#savDat = ["serser_dT", "ppspps_dT", "k1ek1e_dT", "ppsk1e_dT", "ppsser_dT", "ppsklm_dT"]
#titDat = ["Consecutive serial", "Consecutive PPS",
#		"Consecutive single Kalman estimate", "PPS to single Kalman estimate", "PPS to serial", "PPS to new Klm"]
		
pltDat = [ppsk1e_dT  , ppsser_dT  ]
savDat = ["ppsk1e_dT", "ppsser_dT"]
titDat = ["GPS PPS to real-time Kalman estimate", "GPS PPS to serial"]



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

x = [i%4 for i in range(200)]
xc = ts.acf(x)



mplt.rcParams.update({'font.size': 20})
for i in range(len(pltDat)):
	fig = plt.figure(figsize=(12,7))
	
	data = pltDat[i]
	name = savDat[i]
	title = titDat[i]
	
	cor = ts.acf(data, nlags=len(data))
	
	plt.plot(range(len(cor)), cor, c='k')
	plt.title("Autocorrelation for "+title)
	plt.xlabel("Time difference /ms")
	plt.ylabel("Autocorrelation")
	plt.xlim(0,len(data))
	plt.tight_layout()
	
	plt.savefig("../../Results/"+filename+"_"+name+"_Autocor.png", dpi=400)
	plt.show()