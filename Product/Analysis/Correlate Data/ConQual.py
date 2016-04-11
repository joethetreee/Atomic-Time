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
oset_snum = 3

start = 0
end = "end"


def ColArray(N):
	colourNum = np.linspace(0, 1, N)
	colours = [0]*len(colourNum)
	for i in range(len(colours)):
		colours[i] = plt.cm.hot(i)
	return colours

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
qTypes = []
for i in range(len(dataCol[oset_snum])):
	if (dataCol[oset_snum][i] not in qTypes):
		qTypes.append(dataCol[oset_snum][i])
	
serser_dT = [dataCol[oset_ser][i+1]-dataCol[oset_ser][i] for i in range(len(dataRow)-1)]
ppspps_dT = [dataCol[oset_pps][i+1]-dataCol[oset_pps][i] for i in range(len(dataRow)-1)]
k1ek1e_dT = [dataCol[oset_est][i+1]-dataCol[oset_est][i] for i in range(len(dataRow)-1)]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataRow))]

pltDat = [serser_dT  , k1ek1e_dT  , ppsk1e_dT  , ppsser_dT]
savDat = ["serser_dT", "k1ek1e_dT", "ppsk1e_dT", "ppsser_dT"]
titDat = ["Consecutive serial",
		"Consecutive real-time Kalman estimate", "GPS PPS to real-time Kalman estimate", "GPS PPS to serial"]


colArray = ColArray(len(qTypes))
colA = [0]*len(ppsser_dT)
for i in range(len(colA)):
	colA[i] = rgb=colArray[qTypes.index(dataCol[oset_snum][i])][:4]
	
qTypesN = [0]*len(qTypes)
qArr = [0]*len(dataCol[oset_snum])
qMax = max(qTypes)
qMin = min(qTypes)
for i in range(len(qTypes)):
	qTypesN[i] = (qTypes[i]-qMin)/(qMax-qMin)
for i in range(len(qArr)):
	qArr[i] = dataCol[oset_snum][i]
		
def GetOrder(data_):
	# find a measure of spread of data
	# find order of range
	dataRange = max(data)-min(data)
	order = 1
	while(order>dataRange):
		order/=10
	while(order<dataRange):
		order*=10
	order = order/100
		
	return order
	
def GetAvgStd(data_, orderBegin):
	avg = np.average(data_)
	stdDev = np.std(data_)
	j=-orderBegin
	stdDev_ = round(stdDev,j)
	avg_ = round(avg,j)
	while(stdDev_==0 and stdDev>0.00001):
		j+=1
		stdDev_ = round(stdDev,j)
		avg_ = round(avg,j)
	j += 1
	stdDev_ = round(stdDev,j)
	avg_ = round(avg,j)
	if(j<=0):
		stdDev_ = int(stdDev_)
		avg_ = int(avg_)
	return (avg_,stdDev_)

mplt.rcParams.update({'font.size': 20})
for i in range(len(pltDat)):
	
	data = pltDat[i]
	name = savDat[i]
	title = titDat[i]
	qArr_ = qArr
	while(len(qArr_)>len(data)):	qArr_ = qArr_[1:]

	fig = plt.figure(figsize=(12,7))
	
	
	cmap = plt.get_cmap('jet', np.max(qTypes)-np.min(qTypes)+1)
	cbarPlot = plt.scatter(range(0,len(data),1),data,c=qArr_, cmap=cmap,linewidth='0', s=2 ,
						vmin = np.min(qTypes)-.5, vmax = np.max(qTypes)+.5)
	plt.xlim(0,len(data))
	
	order = GetOrder(data)
	order_i = int(round(np.log10(order)))	
	plt.ylim( round((min(data)/order-1)*order,-order_i), round((max(data)/order+1)*order,-order_i) )
	
	cbarTicksTemp = range(min(qTypes), max(qTypes)+1)
	cbar = plt.colorbar(cbarPlot, ticks=cbarTicksTemp)
	
	plt.title(title + " difference by satellite number")
	plt.ylabel("Time difference /ms")
	plt.xlabel("Samples")
	plt.tight_layout()
	
	# correlation on full data and sat num
	# if we are working on serser_dT (diff between same type), arrays have diff length
	startoset = len(dataCol[oset_ser])-len(data)
	print(pearsonr(data, dataCol[oset_snum][startoset:]))

	# now do correlation between averages and sat num
	qAvgArr = [0]*len(qTypes)
	for i in range(startoset,len(data)):
		qAvgArr[qTypes.index(dataCol[oset_snum][i])] += data[i]
	for i in range(len(qTypes)):
		qAvgArr[i]/=dataCol[oset_snum].count(qTypes[i])
	
	print(pearsonr(qAvgArr, qTypes))

	saveFileName = filename+"_"+name+"("+str(start)+"-"+str(end)+")_SatNum"
	plt.savefig("../../Results/"+saveFileName+".png",dpi=400)
	
	plt.show()
	plt.clf()
