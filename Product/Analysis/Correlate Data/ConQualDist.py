# -*- coding: utf-8 -*-
"""
Created on Sat 26 Mar 17:01:47 2016

@author: Duncan

plot differences in time
used to check data

input format:
...
<ser_time>,<pps_time>,<est_time>,<sat_num>
...

doesn't matter which other lines are present; information extracted from t<><> row

"""
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr

filename = "KL1PRD00ChkCor"	

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
oset_snum = 3

normalise = False
start = 0
end = "end"


def ColArray(N):
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours
	

def Median(data):
	tot = sum(data)
	tot_=0
	for i in range(len(data)):
		tot_ += data[i]
		if (tot_>=tot/2):
			return i
			
def GenerateDist(histData_, binMin_, binMax_, binWidth_):
	binNum_ = (binMax_-binMin_)/binWidth_
	binEdges_ = np.linspace(binMin_, binMax_, binNum_)
	binVals_ = np.histogram(histData_, bins=binEdges_)[0]
	
	tot_ = sum(binVals_)
	binVals2_ = [0.]*len(binVals_)
	for k in range(len(binVals_)):
		binVals2_[k] = float(binVals_[k])/tot_	
	
	binMids_ = [0]*len(binVals_)
	for i in range(len(binMids_)):
		binMids_[i] = (binEdges_[i]+binEdges_[1+i])/2.0
		
	return (binVals2_, binMids_)

# put data into arrays
for row in range(len(dataRow)):
	line = contentsTxt[row]
	commaLoc,commaLoc2 = 0,0
	for col in range(parts):
		if (col==parts-1):
			commaLoc2 = len(line)
		else:
			commaLoc2 = commaLoc+line[commaLoc:].index(',')
		dataRow[row][col] = int(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1
		
dataCol = [[0]*len(dataRow) for i in range(parts)]

for row in range(len(dataRow)):
	for col in range(parts):
		dataCol[col][row] = dataRow[row][col]

# find quality types in data
qTypes = []
for i in range(len(dataCol[oset_snum])):
	if (dataCol[oset_snum][i] not in qTypes):
		qTypes.append(dataCol[oset_snum][i])
qTypes.sort()
# find quality types in data
	
serser_dT = [dataCol[oset_ser][i+1]-dataCol[oset_ser][i] for i in range(len(dataRow)-1)]
ppspps_dT = [dataCol[oset_pps][i+1]-dataCol[oset_pps][i] for i in range(len(dataRow)-1)]
k1ek1e_dT = [dataCol[oset_est][i+1]-dataCol[oset_est][i] for i in range(len(dataRow)-1)]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

pltDat = [k1ek1e_dT  , ppsk1e_dT  , ppsser_dT]
savDat = ["k1ek1e_dT", "ppsk1e_dT", "ppsser_dT"]
titDat = ["Consecutive single Kalman estimate", "PPS to single Kalman estimate", "PPS to serial"]

colArray = ColArray(len(qTypes))
colA = [0]*len(ppsser_dT)
for i in range(len(colA)):
	colA[i] = rgb=colArray[qTypes.index(dataCol[oset_snum][i])][:3]
	
qTypesN = [0]*len(qTypes) 							# quality types normalised up to 1.0
qTypesNZ = [0]*len(qTypes) 						# quality types normalised between 0.0->1.0
qArrN = [0]*len(dataCol[oset_snum])
qArrNZ = [0]*len(dataCol[oset_snum])
qMax = max(qTypes)
qMin = min(qTypes)
for i in range(len(qTypes)):
	qTypesN[i] = qTypes[i]/qMax
	qTypesNZ[i] = (qTypes[i]-qMin)/(qMax-qMin)
for i in range(len(qArrN)):
	qArrN[i] = dataCol[oset_snum][i]/qMax
	qArrNZ[i] = (dataCol[oset_snum][i]-qMin)/(qMax-qMin)
	
for i in range(len(pltDat)):
	data = pltDat[i]
	name = savDat[i]
	title = titDat[i]
	qArr = qArrN
	
	osetStart = len(dataCol[oset_snum])-len(data)
	data_ = [[] for i in range(len(data))]
	for i in range(len(data)):
		data_[qTypes.index(dataCol[oset_snum][osetStart+i])].append(data[i])

	fig = plt.figure(figsize=(11,6))
	
	# find a measure of spread of data
	# find order of range
	dataRange = max(data)-min(data)
	order = 1
	while(order<dataRange):
		order*=10
	order/=10
	if (order>1):	order/=10
		
	binMin = int(min(data)/order-1)*order
	binMax = int(max(data)/order+5)*order 			# +5 so we have space for text
	binNum = binMax-binMin
	ser_leg = [0]*len(qTypes)
	txt_leg = [str(i) for i in qTypes]
	
	# plot a scatter plot so we can get our colours for the colour bar (can't do with plt.plot); discard
	qArrNZ_ = qArrNZ[osetStart:]
	cbarPlot = plt.scatter(range(0,len(data),1),data,c=qArrNZ_, cmap=plt.cm.gist_rainbow,linewidth='0', s=8)
	plt.clf()
	fig = plt.figure(figsize=(11,6))
	mplt.rcParams.update({'font.size': 14})

	medianArr = [0]*len(qTypesNZ)
	avgValx_type = [0]*len(qTypesNZ) 				# store the average value for each "delimiter"
	avgValu_type = [0]*len(qTypesNZ) 				# store the std dev for each "delimiter"
	for j in range(len(qTypesNZ)):
		histData = data_[j]
		binWidth = (binMax - binMin)/binNum
		binEdges = np.linspace(binMin, binMax, binNum)
		
		binVals = np.histogram(histData, bins=binEdges)[0]
		binMids = [0]*len(binVals)
		binVals2 = [0.]*len(binVals)
		
		if (normalise):
			tot = sum(binVals)
			for k in range(len(binVals)):
				binVals2[k] = float(binVals[k])/tot
			binVals = binVals2
		
		for i in range(len(binMids)):
			binMids[i] = (binEdges[i]+binEdges[1+i])/2.0
			
		#print(qTypes[j])
			
		ser_leg[j] ,= plt.plot(binMids, binVals, color=plt.cm.gist_rainbow(qTypesNZ[j]))
		medianArr[j] = binMids[Median(binVals)]
		tot=0
		for i in range(len(binVals)):
			tot += float(binMids[i]*binVals[i])/sum(binVals)
		std=0
		for i in range(len(binVals)):
			std += float((binMids[i]-tot)**2)*binVals[i]/sum(binVals)
		std = np.sqrt(std)
		avgValx_type[j] = tot
		avgValu_type[j] = std
		#plt.plot([tot,tot],[0,max(binVals)], color=plt.cm.gist_rainbow(qTypesNZ[j]))
	print(pearsonr(medianArr, qTypes))
	
	ylim = plt.gca().get_ylim()
	xlim = plt.gca().get_xlim()
	
	for j in range(len(qTypes)):
		plt.annotate('sat# '+str(qTypes[j])+' avg '+str(round(avgValx_type[j],1))+' std '+str(round(avgValu_type[j],1))+' ms'
		, xy=(0.5,0.1+0.8*j/len(qTypes)), xycoords='axes fraction')	
		
	plt.title("Dist. of "+title+" difference by satellite number")
	plt.xlabel("Time difference /ms")
	plt.ylabel("Frequency")
	
	cbarTicksTemp = np.linspace(min(qTypesNZ), max(qTypesNZ), len(qTypesNZ))
	cbar = plt.colorbar(cbarPlot, ticks=cbarTicksTemp)
	cbarTicksNew = np.linspace(min(qTypes), max(qTypes), len(qTypes), dtype = int)
	cbar.ax.set_yticklabels(cbarTicksNew)  # horizontal colorbar
	
	saveFileName = filename+"_"+name+"_SatNum_dist"
	plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
	plt.savefig("../../Results/"+saveFileName+".svg")
	
	plt.show()
	
	print(pearsonr(ppsser_dT, qArr))