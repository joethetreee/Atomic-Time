# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:19:25 2015

@author: Duncan

Assess estimators of second length

format:
lines must contain
txxxx...,xxxx... (times for serial,pps)

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plttick
import KalmanFilter as kal
filename = "GPSMIL33ChckdCor"

# Kalman data
um = 150 			# uncertainty in measurement
ue = 0.5				# uncertainty in estimation



# extract data into arrays

contents = open(filename+".txt", mode='r')
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

##Distribution stuff
#
#estDifEnd = []
#estAvg = []
#estCCor = []
#act = []
#xstep = 50
#for i in range(0,len(ser_T0),xstep):
#	x = range(0, min(len(ser_T0)-1,i+xstep)-i,1)
#	if (len(x)<3):
#		continue
#	y = ser_T0[i:i+x[-1]+1]
#	y = [y[j]-y[0] for j in range(len(y))]
#	z = pps_T0[i:i+x[-1]+1]
#	z = [z[j]-z[0] for j in range(len(z))]
#	ccor = CrossCor(x, y)/CrossCor(x, x)
#	avg = 0
#	for i in range(len(x)):
#		if (x[i]==0): avg += 1000
#		else: avg += y[i]/x[i]
#	avg /= len(x)
#	avgEnd = (y[-1]-y[0])/(len(y)-1)
#	actT = (z[-1]-z[0])/(len(z)-1)
#	
#	estDifEnd.append(avgEnd)
#	estAvg.append(avg)
#	estCCor.append(ccor)
#	act.append(actT)
#	
#dataTypes = [estDifEnd,"End Time Difference",estAvg,"Average Ticks",estCCor,"Cross Correlation"]
#
#binMin = 999
#binMax = 1002
#binWidth = 0.05
#binNum = (binMax-binMin)/binWidth
#binEdges = np.linspace(binMin,binMax,binNum+1)
#binMids = [(binEdges[i+1]+binEdges[i])/2 for i in range(len(binEdges)-1)]
#
#for i in range(0, len(dataTypes), 2):
#	data = dataTypes[i]
#	binVals = np.histogram(data, bins=binEdges)[0]
#	
#	plt.figure()
#	ax = plt.gca()
#	ax.plot(binMids,binVals)
#	plt.title("Second estimation using "+dataTypes[i+1]+" sample length "+str(xstep))
#	plt.xlabel("second length / ms")
#	plt.ylabel("frequency")
#	x_formatter = plttick.ScalarFormatter(useOffset=False)
#	ax.xaxis.set_major_formatter(x_formatter)
#	plt.annotate("actual "+str(round(np.average(act),2))+"+/-"+str(round(np.std(act),2))+
#		";  estimator "+str(round(np.average(data),2))+"+/-"+str(round(np.std(data),2))+
#		";  MSE "+str(round(np.sqrt((np.average(data)-np.average(act))**2+np.std(data)**2),2)),
#		xy=(0.05, 0.95), xycoords='axes fraction')
#	plt.savefig(filename+"Estimator "+dataTypes[i+1]+"_smpl"+str(xstep)+".png", dpi=600, facecolor='w', edgecolor='w',
#	        orientation='portrait', papertype=None, format=None,
#	        transparent=False, bbox_inches=None, pad_inches=0.1,
#	        frameon=None)

#Length effect stuff

mseDifEnd = []
mseAvg = []
mseCCor = []
mseKal1 = [] 		# average two values then do cross correlation
xArr = []
for xstep_ in range(1,8):
	estDifEnd = []
	estAvg = []
	estCCor = []
	estKal1 = []
	act = []
	xstep = int(np.exp(xstep_))
	
	for i in range(0,len(ser_T0),xstep):
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

		ky = [0]*len(y)
		ku = [um]*len(y)
		for i in range(1,len(x)):
			(ky[i],ku[i]) = kal.KalFilIter(ky[i-1],1000,y[i],ku[i-1],ue,um,1,1,1)
		avgEndKal1 = (ky[-1]-ky[0])/(len(y)-1)
#		ky = [0]*len(y)
#		ku = [um]*len(y)
#		for i in range(1,len(x)):
#			(ky[i],ku[i]) = kal.KalFilIter(ky[i-1],avgEndKal1,y[i],ku[i-1],ue,um,1,1,1)
#		avgEndKal1 = (ky[-1]-ky[0])/(len(y)-1)
		
		estDifEnd.append(avgEnd)
		estAvg.append(avg)
		estCCor.append(ccor)
		estKal1.append(avgEndKal1)
		act.append(actT)
	xArr.append(xstep)
	mseDifEnd.append(np.sqrt((np.average(act)-np.average(estDifEnd))**2+np.std(estDifEnd)**2))
	mseAvg.append(np.sqrt((np.average(act)-np.average(estAvg))**2+np.std(estAvg)**2))
	mseCCor.append(np.sqrt((np.average(act)-np.average(estCCor))**2+np.std(estCCor)**2))
	mseKal1.append(np.sqrt((np.average(act)-np.average(estKal1))**2+np.std(estKal1)**2))
	#print(xArr[-1],mseDifEnd[-1],mseAvg[-1],mseCCor[-1])

#log
ser_difEnd ,= plt.plot(np.log(xArr),np.log(mseDifEnd))
ser_avg ,= plt.plot(np.log(xArr),np.log(mseAvg))
ser_cCor ,= plt.plot(np.log(xArr),np.log(mseCCor))
ser_Kal1 ,= plt.plot(np.log(xArr),np.log(mseKal1))

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
plt.legend([ser_difEnd,ser_avg,ser_cCor,ser_Kal1],["End point difference","Average",
		"Cross correlation","Kalman, end diff"])
plt.savefig(filename+"EstimatorMSE.png", dpi=600, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None)