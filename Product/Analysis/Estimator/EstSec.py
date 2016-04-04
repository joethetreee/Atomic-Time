# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 13:19:25 2015

@author: Duncan

Assess estimators of second length

format:
lines must contain
txxxx...,xxxx... (times for serial,pps)

"""
import numpy as np
import matplotlib.pyplot as plt
import KalmanFilter as kal

from EstSec_by_dist import MinimiseWidth

filename = "GPSMIL33ChckdCor"

# Kalman data
um = 150 			# uncertainty in measurement
ue = 0.5				# uncertainty in estimation



# extract data into arrays

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

def CrossCor(x,y):
	length = min(len(x),len(y))
	cor = 0
	for i in range(length):
		cor += x[i]*y[i]
	return cor

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
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]

ser_T0 = [ser_T[i]-ser_T[0] for i in range(len(ser_T))]
pps_T0 = [pps_T[i]-pps_T[0] for i in range(len(ser_T))]

mseDifEnd = []
mseAvg = []
mseCCor = []
mseKal1 = [] 		# average two values then do cross correlation
mseDist = [] 		# from minimising distribution width
xArr = []

xfactor = 1.5
xstart = 2
xstop = int(np.log(len(ser_T0)/3)/np.log(xfactor))

for xstep_ in range(xstart,xstop):
	print(xstep_)
	estDifEnd = []
	estAvg = []
	estCCor = []
	estKal1 = []
	estDist = []
	act = []
	xstep = int(xfactor**xstep_)
	
	for i in range(0,len(ser_T0),xstep):
		if (len(act)>=100): 						# we don't need to repeat too many times
			break
		print(i,xstep)
		x = range(0, min(len(ser_T0)-1,i+xstep)-i,1)
		if (len(x)<xstep):
			continue
		y = ser_T0[i:i+x[-1]+1]
		y = [y[j]-y[0] for j in range(len(y))]
		z = pps_T0[i:i+x[-1]+1]
		z = [z[j]-z[0] for j in range(len(z))]
		ccor = CrossCor(x, y)/CrossCor(x, x)
		y2 = [(y[i]+y[i+1]) for i in range(0,2*int(len(y)/2),2)]
		x2 = [(x[i]+x[i+1])/2 for i in range(0,2*int(len(x)/2),2)]
		
		avg = 0
		for i in range(len(x)):
			if (x[i]==0): avg += 1000
			else: avg += y[i]/x[i]
		avg /= len(x)
		avgEnd = (y[-1]-y[0])/(len(y)-1)
		#actT = (z[-1]-z[0])/(len(z)-1)
		actT = CrossCor(x, z)/CrossCor(x, x)

		kalIter = 20 			# number of datapoints to filter
		kalIter = min(kalIter,int(len(y)/2)-1)
		ky = [y[kalIter],y[-kalIter-1]] 	# start and end filtered values
		ku = [150,150]
		for i in range(0,kalIter):
			(ky[1],ku[1]) = kal.KalFilIter(ky[1],1000,y[-kalIter+i],ku[1],ue,um,1,1,1)
			(ky[0],ku[0]) = kal.KalFilIter(ky[0],-1000,y[kalIter-1-i],ku[0],ue,um,1,1,1)
		avgEndKal1 = (ky[1]-ky[0])/(len(y)-1)
		
		#avgDist = MinimiseWidth(y)[0]
		
#		ky = [0]*len(y)
#		ku = [um]*len(y)
#		for i in range(1,len(x)):
#			(ky[i],ku[i]) = kal.KalFilIter(ky[i-1],avgEndKal1,y[i],ku[i-1],ue,um,1,1,1)
#		avgEndKal1 = (ky[-1]-ky[0])/(len(y)-1)
		
		estDifEnd.append(avgEnd)
		estAvg.append(avg)
		estCCor.append(ccor)
		estKal1.append(avgEndKal1)
		#estDist.append(avgDist)
		act.append(actT)
	xArr.append(xstep)
	mseDifEnd.append(np.sqrt((np.average(act)-np.average(estDifEnd))**2+np.std(estDifEnd)**2))
	mseAvg.append(np.sqrt((np.average(act)-np.average(estAvg))**2+np.std(estAvg)**2))
	mseCCor.append(np.sqrt((np.average(act)-np.average(estCCor))**2+np.std(estCCor)**2))
	mseKal1.append(np.sqrt((np.average(act)-np.average(estKal1))**2+np.std(estKal1)**2))
	#mseDist.append(np.sqrt((np.average(act)-np.average(estDist))**2+np.std(estDist)**2))
	#print(xArr[-1],mseDifEnd[-1],mseAvg[-1],mseCCor[-1])

#log
ser_difEnd ,= plt.plot(np.log(xArr),np.log(mseDifEnd))
ser_avg ,= plt.plot(np.log(xArr),np.log(mseAvg))
ser_cCor ,= plt.plot(np.log(xArr),np.log(mseCCor))
ser_kal1 ,= plt.plot(np.log(xArr),np.log(mseKal1))
#ser_dist ,= plt.plot(np.log(xArr),np.log(mseDist))

##linear
#ser_difEnd ,= plt.plot(xArr,mseDifEnd)
#ser_avg ,= plt.plot(xArr,mseAvg)
#ser_cCor ,= plt.plot(xArr,mseCCor)
#ser_avg2CCor ,= plt.plot(xArr,mseAcg2CCor)

plt.title("Mean Squared Error of various second length estimators")
#log
plt.xlabel("Sample size")
plt.ylabel("MSE / ms")
#linear
plt.xlabel("log of Sample size")
plt.ylabel("log of (MSE / ms)")
plt.legend([ser_difEnd,ser_avg,ser_cCor,ser_kal1],["End point difference","Average",
		"Cross correlation","Kalman, end diff"])
#plt.savefig(filename+"EstimatorMSE.png", dpi=600, facecolor='w', edgecolor='w',
#        orientation='portrait', papertype=None, format=None,
#        transparent=False, bbox_inches=None, pad_inches=0.1,
#        frameon=None)