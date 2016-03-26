# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 13:21:11 2015

@author: Duncan

Estimate PPS time for working data using template PPS-Serial data

PPS-Serial data is characterised using a property in the reference data e.g. satellite fix number
A prediction of PPS is generated from working data with considerations to the property

The property is labelled with <q>
"""

import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import KalmanFilter as klm
	

start = 0
end = "end"

filenameR = "GPSMIL37ChckdCor" 	# cast filename
oset_GGAR = 0 				# offset of GGA sentence
oset_PPSR = 2 				# offset of PPS sentence
periodR = 3	 				# number of lines in each data set
qCommaIndexR= 7				# number of commas in GGA line before data

filename = "GPSMIL33ChckdCor" 	# filename of data do be cast
oset_GGA = 0 				# offset of GGA sentence
oset_PPS = 2 				# offset of PPS sentence
period = 3	 				# number of lines in each data set
qCommaIndex = 7				# number of commas in GGA line before data

# extract data into arrays

contentsR = open("../../Results/"+filenameR+".txt", mode='r')
contentsTxtR = contentsR.readlines()
contentsR.close()

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

start = period*int(max(0,start)/period)
if (end=="end"):
	end = int(len(contentsTxt)/period)
else: end = period*int(min(len(contentsTxt),end)/period)
ser_T = [0]*(end-start) 	 	# PPS times for data
pps_T = [0]*(end-start) 	 	# serial times for data
qVals = [] 						# list of different qValues (properties)

ser_TR = [0]*len(contentsTxtR) 	# PPS times for reference
pps_TR = [0]*len(contentsTxtR) 	# serial times for reference
qValsR = [] 					# list of different qValues (properties)

# Collect serial, PPS times into array and compile a list of all q types

j = 0
for i in range(start, end, 1):
	line = contentsTxt[i*period+oset_GGA]
	commaLoc = 0
	#print("0", line, i*period+oset_GGA)
	if (line[:6]=="$GPGGA"):
		for commaNum in range(qCommaIndex): 	 	 	# value of interest
			commaLoc += line[commaLoc:].index(',')+1
		commaLoc2 = commaLoc + line[commaLoc:].index(',')
		qVal = int(line[commaLoc:commaLoc2])
		if qVal not in qVals:
			qVals.append(qVal)
	line = contentsTxt[i*period+oset_PPS]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]

j = 0
for i in range(0,int(len(contentsTxtR)/periodR),1):
	line = contentsTxtR[i*periodR+oset_GGAR]
	#print("0", line, i*periodR+oset_GGAR )
	commaLoc = 0
	if (line[:6]=="$GPGGA"):
		for commaNum in range(qCommaIndexR): 	 	 	# value of interest
			commaLoc += line[commaLoc:].index(',')+1
		commaLoc2 = commaLoc + line[commaLoc:].index(',')
		qVal = int(line[commaLoc:commaLoc2])
		if qVal not in qValsR:
			qValsR.append(qVal)
	line = contentsTxtR[i*periodR+oset_PPSR]
	#print("1", line, i*periodR+oset_PPSR)
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_TR[j] = int(line[1:commaLoc])
		pps_TR[j] = int(line[commaLoc+1:])
		j += 1
ser_TR = ser_TR[:j]
pps_TR = pps_TR[:j]

timing_PPS = False

# sort q types and then collect a sequential order of all appearances for association with times

qVals.sort()
qValsR.sort()
print(qVals)
print(qValsR)


q_T = [0]*len(ser_T)
q_TR = [0]*len(ser_TR)

	 # store sequential list of working q values to associate with serial times
for i in range(start, end, 1):
	line = contentsTxt[i*period+oset_GGA]
	commaLoc = 0
	if (line[:6]=="$GPGGA"):
		for commaNum in range(qCommaIndex): 	 	 	# value of interest
			commaLoc += contentsTxt[i*period+oset_GGA][commaLoc:].index(',')+1
		commaLoc2 = commaLoc + contentsTxt[i*period+oset_GGA][commaLoc:].index(',')
		qVal = line[commaLoc:commaLoc2]
		q_T[int(i)] = int(qVal)
	
	# store reference data: want an array of pps-ser times for each q value
ppsser_dTR = [[] for i in range(len(qValsR))] 			# stores pps-ser reference times by q value
for i in range(0, len(ser_TR), 1):
	line = contentsTxtR[i*periodR+oset_PPSR]
	ppsser_dt = 0
	commaLoc = 0
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ppsser_dt = int(line[1:commaLoc])-int(line[commaLoc+1:])
		
	line = contentsTxtR[i*periodR+oset_GGAR]
	commaLoc = 0
	if (line[:6]=="$GPGGA"):
		for commaNum in range(qCommaIndexR): 	 	 	# value of interest
			commaLoc += contentsTxtR[i*periodR+oset_GGAR][commaLoc:].index(',')+1
		commaLoc2 = commaLoc + contentsTxtR[i*periodR+oset_GGAR][commaLoc:].index(',')
		qVal = int(line[commaLoc:commaLoc2])
		ppsser_dTR[qValsR.index(qVal)].append(ppsser_dt)

print(len(ppsser_dTR))
ppsser_xR = [np.average(ppsser_dTR[i]) for i in range(len(ppsser_dTR))]
ppsser_uR = [np.std(ppsser_dTR[i]) for i in range(len(ppsser_dTR))]

# append properties of qValsR that don't actually appear -- copy in closest match
j=0
for i in range(len(qVals)):
	j=min(j,len(qValsR)-1)
	while (qValsR[j]<=qVals[i]):
		j=j+1
		if (j>=len(qValsR)):
			break
	j-=1
	print("test",i,j,qVals[i],qValsR[j],"  ",len(qVals),min(qVals),max(qVals),"  ",len(qValsR),min(qValsR),max(qValsR))
	if (qValsR[j]!=qVals[i]): 			# happens if the qVal doesn't appear in qValsR
		if (j==0):					# if the new value goes at the start
			ppsser_xR.insert(j,ppsser_xR[j])
			ppsser_uR.insert(j,ppsser_uR[j])
			qValsR.insert(j,qVals[i])
		elif (j>=len(qValsR)-1):		# if the new value goes at the end
			ppsser_xR.append(ppsser_xR[j])
			ppsser_uR.append(ppsser_uR[j])
			qValsR.append(qVals[i])
		else: 	 	 	 	 	 	# if the new value goes midway
			ppsser_xR.insert(j,ppsser_xR[j-1]+(ppsser_xR[j]-ppsser_xR[j-1])*
					(qVal[i]-qValsR[j-1])/(qValsR[j]-qValsR[j-1]))
			ppsser_uR.insert(j,ppsser_uR[j-1]+(ppsser_uR[j]-ppsser_uR[j-1])*
					(qVal[i]-qValsR[j-1])/(qValsR[j]-qValsR[j-1]))
			qValsR.insert(j,qVals[i])

ppsE_T = [0]*len(ser_T)	 	# expected time of serial arrival
covU_T = [0]*len(ser_T)	 	# expected uncertainty
ardU_t = 0.5					# uncertainty in arduino times
#ardD_t = (ser_T[-1]-ser_T[0])/(len(ser_T)-1)-1000 	# arduino drift per millisecond (from post-analysis)
ardD_t = 0.0005
secLen = 1000
secLenU = 1
	
covU_T[0] = 50
ppsE_T[0] = ser_T[0]-ppsser_xR[qValsR.index(q_T[0])]

for i in range(len(ser_T)-1):
	if (i>0):
		(secLen,secLenU) = klm.KalFilIter(secLen, 0, ppsE_T[i]-ppsE_T[i-1], secLenU, ardD_t, covU_T[i])
	#print(secLen,secLenU)
	qValiCur = qValsR.index(q_T[i])
	qValiNext = qValsR.index(q_T[1+i])
	ppsE_T[1+i], covU_T[1+i] = klm.KalFilIter(ppsE_T[i], secLen+ardD_t-(ppsser_xR[qValiNext]-ppsser_xR[qValiCur]),
									ser_T[1+i]-ppsser_xR[qValiNext], covU_T[i], ardU_t, ppsser_uR[qValiNext])
	covU_T[1+i] = np.sqrt(covU_T[1+i]**2+0.5**2)							
	#print(1000+ardD_t-(ppsser_xR[qValiNext]-ppsser_xR[qValiCur]), (ser_T[1+i]-ppsser_xR[qValiNext])-(ser_T[i]-ppsser_xR[qValiCur]))

ppsser_dT = [ser_T[i]-pps_T[i] for i in range(len(ser_T))]

qValsN = [0]*len(qVals)
q_TN = [0]*len(q_T)
qMax = max(qVals)
qMin = min(qVals)
for i in range(len(qVals)):
	qValsN[i] = (qVals[i]-qMin)/(qMax-qMin)
for i in range(len(q_T)):
	q_TN[i] = (q_T[i]-qMin)/(qMax-qMin)

mplt.rcParams.update({'font.size': 15})
fig = plt.figure(figsize=(11,6))

ppsppsE_dT = [ppsE_T[i]-pps_T[i] for i in range(len(ppsE_T))]
ppsESecLen = (ppsE_T[-1]-ppsE_T[0])/(len(ppsE_T)-1)
secppsE_dT = [ppsE_T[i]-i*ppsESecLen for i in range(len(ppsE_T))]
ppsUSecLen = np.std(secppsE_dT)


ppsEE_T = [ppsE_T[0]]*len(ppsE_T)
ppsEU_T = [ppsUSecLen]*len(covU_T)

#secLenGroupSize = 2000
#for i in range(len(ppsppsE_dT)-1):
#	ppsESecLen = 1000
#	ppsESecLenU = 0.5
#	if (i>secLenGroupSize):
#		ppsESecLen = (ppsE_T[i]-ppsE_T[i-secLenGroupSize])/(secLenGroupSize)
#		ppsESecLenU = 0.5
#	(ppsEE_T[i+1],ppsEU_T[i+1]) = klm.KalFilIter(ppsEE_T[i],ppsESecLen,ppsE_T[i+1], ppsEU_T[i],ppsESecLenU,ppsUSecLen)

ppsESecLenE = 1000
ppsESecLenU = 1

secLenGroupSize = 2000
for i in range(len(ppsppsE_dT)-1):
	if (i>secLenGroupSize):
		ppsESecLenE_ = (ppsE_T[i]-ppsE_T[i-secLenGroupSize])/(secLenGroupSize)
		ppsESecLenU_ = np.std(secppsE_dT[i-secLenGroupSize:i])/secLenGroupSize
		(ppsESecLenE,ppsESecLenU) = klm.KalFilIter(ppsESecLenE,0,ppsESecLenE_, ppsESecLenU,0.01*secLenGroupSize/10000,ppsESecLenU_)
		#print(ppsESecLenE,ppsESecLenU,ppsESecLenE_,ppsESecLenU_)
		#(ppsESecLenE,ppsESecLenU) = (ppsESecLenE_,0.001)
	(ppsEE_T[i+1],ppsEU_T[i+1]) = klm.KalFilIter(ppsEE_T[i],ppsESecLen,ppsE_T[i+1], ppsEU_T[i],ppsESecLenU,ppsUSecLen)

ppsppsEE_dT = [ppsEE_T[i]-pps_T[i] for i in range(len(ppsEE_T))]

mplt.rcParams.update({'font.size': 16})
fig = plt.figure(figsize=(10,6))
s = plt.scatter(range(0, len(ppsppsE_dT)), ppsppsE_dT, c=q_TN, cmap=plt.cm.gist_rainbow , linewidth='0', s=2)
plt.xlim(0,len(ppsppsE_dT)-1)

plt.title("PPS prediction from Kalman filter with #sat")
plt.xlabel("Samples")
plt.ylabel("PPS_pred - PPS_act / ms")
#plt.scatter(range(0, len(ppsser_dT)), ppsser_dT, c='k', linewidth='0', s=2)
cbarTicksTemp = np.arange(min(qValsN), max(qValsN)+0.00001, 1.0/(max(qVals)-min(qVals)))
cbarTicksNew = range(min(qVals), max(qVals)+1, 1)
cbar = plt.colorbar(s, ticks=cbarTicksTemp)
cbar.ax.set_yticklabels(cbarTicksNew)  # horizontal colorbar

plt.annotate("Avg: "+str(round(np.average(ppsppsE_dT),1))+" ms;  std dev: "+
			str(round(np.std(ppsppsE_dT),1))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
saveFileName = filename+"("+str(start)+"-"+str(end)+")"+"KalCor1_"+filenameR+"_Causal"

plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
plt.savefig("../../Results/"+saveFileName+".svg")

fig = plt.figure(figsize=(10,6))
s = plt.scatter(range(0, len(ppsppsEE_dT)), ppsppsEE_dT, c=q_TN, cmap=plt.cm.gist_rainbow , linewidth='0', s=2)
plt.xlim(0,len(ppsppsEE_dT)-1)

plt.title("PPS prediction from double Kalman filter with #sat")
plt.xlabel("Samples")
plt.ylabel("PPS_pred - PPS_act / ms")
#plt.scatter(range(0, len(ppsser_dT)), ppsser_dT, c='k', linewidth='0', s=2)
cbarTicksTemp = np.arange(min(qValsN), max(qValsN)+0.00001, 1.0/(max(qVals)-min(qVals)))
cbarTicksNew = range(min(qVals), max(qVals)+1, 1)
cbar = plt.colorbar(s, ticks=cbarTicksTemp)
cbar.ax.set_yticklabels(cbarTicksNew)  # horizontal colorbar

plt.annotate("Avg: "+str(round(np.average(ppsppsEE_dT),1))+" ms;  std dev: "+
			str(round(np.std(ppsppsEE_dT),1))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
saveFileName = filename+"("+str(start)+"-"+str(end)+")"+"KalCor2_"+filenameR+"_Causal"

plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
plt.savefig("../../Results/"+saveFileName+".svg")

print(cbarTicksTemp)
print(cbarTicksNew)
	
#mplt.rcParams.update({'font.size': 18})
#fig = plt.figure(figsize=(10,6))
##plt.plot(binMids, binValsC)
##plt.plot(binMids, binVals)
##ser_ppsser, = plt.plot(ppsser_dT)
#uncertArrL = [ppsppsP_dT[i]-uncertArr[i] for i in range(len(ppsppsP_dT))]
#uncertArrH = [ppsppsP_dT[i]+uncertArr[i] for i in range(len(ppsppsP_dT))]
#ser_ppsppsP ,= plt.plot(range(len(ppsppsP_dT)),ppsppsP_dT, color="k",linewidth=2)
#ser_ppsppsPL ,= plt.plot(range(len(ppsppsP_dT)),uncertArrL, "r--", color="k",linewidth=1)
#ser_ppsppsPH ,= plt.plot(range(len(ppsppsP_dT)),uncertArrH, "r--", color="k",linewidth=1)
#plt.xlim(0,len(ppsppsP_dT))
##ser_ppsppsPF, = plt.plot(ppsppsPF_dT)
#plt.xlabel("Samples")
#plt.ylabel("PPS prediction accuracy /ms")
#plt.title("PPS prediction using distribution profile")
#plt.legend([ser_ppsppsP, ser_ppsppsPH], ["PPS-prediction", "Uncertainty band"], loc="lower right")
#params = {'legend.fontsize': 18}
#plt.rcParams.update(params)    # the legend text fontsize
##plt.annotate("Cast "+filenameC+"; data "+filename+" "+str(int(start/1000))+"k-"+str(int(end/1000))+
##	"k_"+str(int(sampleSize/1000))+"k; second len Ser end dif", xy=(0.05, 0.95), xycoords='axes fraction')
#plt.annotate("Avg: "+str(round(np.average(ppsppsP_dT),1))+" ms;  std dev: "+
#			str(round(np.std(ppsppsP_dT),1))+" ms", xy=(0.05, 0.95), xycoords='axes fraction')
#saveFileName = filename+"("+str(start)+"-"+str(end)+")"+"CompDist"+filenameC+"_serTime="+str(not timing_PPS)
#plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
#plt.savefig("../../Results/"+saveFileName+".svg")
#
#
#plt.show()