# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:19:25 2015

@author: Duncan

Use a Kalman filter on GPS serial data to predict the PPS arrial time

Kalman filter smooths time of GPS serial data arrival, use PPS-SER distribution average to get expected PPS time

We must supply uncertainties in GPS serial time (given by PPS_SER dist) and arduino time (~1 ms)
Also we use the *drift* on the arduino -- the average second length discrepency

format:
lines must contain
txxxx...,xxxx... (times for serial,pps)

"""
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import KalmanFilter as klm
filename = "GARNMEA20160131_190024ChckdCor"

# extract data into arrays

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt)
pps_T = [0]*len(contentsTxt)

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
start = 0		
end = j
ser_T = ser_T[start:end]
pps_T = pps_T[start:end]


serE_T = [0]*len(ser_T)	 	# expected time of serial arrival
covU_T = [0]*len(ser_T)	 	# expected uncertainty
ardU_t = 0.5				# uncertainty in arduino times
ardD_t = (pps_T[-1]-pps_T[0])/(len(pps_T)-1)-1000	# arduino drift per millisecond (from post-analysis) - defined as ard_ms in 1s - 1000
serU_t = 150			 	# uncertainty in gps serial arrival times
	
covU_T[0] = 100
serE_T[0] = ser_T[0]

for i in range(len(serE_T)-1):
	serE_T[1+i], covU_T[1+i] = klm.KalFilIter(serE_T[i], 1000+ardD_t, ser_T[1+i], covU_T[i], ardU_t, serU_t)
	
ppsserE_dT = [0]*len(serE_T)
for i in range(len(serE_T)):
	ppsserE_dT[i] = serE_T[i]-pps_T[i]
	
ppsser_dT = [0]*len(ser_T)
for i in range(len(ppsser_dT)):
	ppsser_dT[i] = ser_T[i]-pps_T[i]
	
	
serser_dT = [0]*(len(ser_T)-1)
for i in range(len(serser_dT)):
	serser_dT[i] = ser_T[1+i]-ser_T[i]
	
	
ppspps_dT = [0]*(len(ser_T)-1)
for i in range(len(serser_dT)):
	ppspps_dT[i] = pps_T[1+i]-pps_T[i]
	
	
serEserE_dT = [0]*(len(serE_T)-1)
for i in range(len(serEserE_dT)):
	serEserE_dT[i] = serE_T[1+i]-serE_T[i]
	

mplt.rcParams.update({'font.size': 16})
fig = plt.figure(figsize=(10,6))

yLow = min(min(ppsser_dT),min(ppsserE_dT))
yHi = max(max(ppsser_dT),max(ppsserE_dT))
yLow = max(0, int(yLow/20)*20)
yHi = min(1000, int(yHi/20+1)*20)
	
xplot = np.linspace(0,len(ppsser_dT),len(ppsser_dT))
ser_ppsser = plt.scatter(xplot, ppsser_dT, s=2, linewidth=0, color="black")
ser_ppsserE = plt.scatter(xplot, ppsserE_dT, s=2, linewidth=0, color="red")
plt.xlim(min(xplot),max(xplot))
plt.ylim(yLow,yHi)
plt.title("PPS Serial difference using Kalman filter")
plt.xlabel("Sample")
plt.ylabel("Time difference / ms")
lgndh = plt.legend([ser_ppsser,ser_ppsserE],["Raw","Kalman"])
lgndh.legendHandles[0]._sizes = [30]
lgndh.legendHandles[1]._sizes = [30]
params = {'legend.fontsize': 18}
plt.rcParams.update(params)    # the legend text fontsize
plt.annotate("std dev "+str(int(round(np.std(ppsser_dT),0)))+
	 " --> "+str(int(round(np.std(ppsserE_dT),0)))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
plt.savefig("../../Results/"+filename+"ppsserKalman("+str(start)+"-"+str(end)+").png",dpi=400)
plt.savefig("../../Results/"+filename+"ppsserKalman("+str(start)+"-"+str(end)+").svg")


fig = plt.figure(figsize=(10,6))
	
yLow = min(min(serser_dT),min(serEserE_dT))
yHi = max(max(serser_dT),max(serEserE_dT))
yLow = max(0, int(yLow/20)*20)
yHi = min(2000, int(yHi/20+1)*20)

xplot = np.linspace(0,len(serser_dT),len(serser_dT))
ser_serser = plt.scatter(xplot, serser_dT, s=2, linewidth=0, color="black")
ser_serEserE = plt.scatter(xplot, serEserE_dT, s=2, linewidth=0, color="red")
plt.xlim(min(xplot),max(xplot))
plt.ylim(yLow,yHi)
plt.title("Consecutive serial time difference using Kalman filter")
plt.xlabel("Sample")
plt.ylabel("Time difference / ms")
lgndh = plt.legend([ser_serser,ser_serEserE],["Raw","Kalman"])
lgndh.legendHandles[0]._sizes = [30]
lgndh.legendHandles[1]._sizes = [30]
params = {'legend.fontsize': 18}
plt.rcParams.update(params)    # the legend text fontsize
plt.annotate("std dev "+str(int(round(np.std(serser_dT),0)))+
	 " --> "+str(round(np.std(serEserE_dT),1))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
plt.savefig("../../Results/"+filename+"serserKalman("+str(start)+"-"+str(end)+").png",dpi=400)
plt.savefig("../../Results/"+filename+"serserKalman("+str(start)+"-"+str(end)+").svg")