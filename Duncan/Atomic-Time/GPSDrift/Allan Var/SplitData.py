import matplotlib.pyplot as plt
import numpy as np

filename = "PPSSer12"
filenameExt = filename+".txt"

contents = open(filenameExt, mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt)
pps_T = [0]*len(contentsTxt)

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (',' in line):
		commaLoc = line.index(',')
		ser_T[j] = int(line[:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j+1]
pps_T = pps_T[:j+1]

serpps_dT = [0]*(len(ser_T))

for i in range(len(ser_T)):
	serpps_dT[i] = ser_T[i]-pps_T[i]


poolCentre = []		# pools data together in groups of size poolSize
poolAvg = []
poolStdDev = []
poolSize = 30		# size of pools to test for boundaries

for i in range(int(len(serpps_dT)/poolSize)):
	dataTest = serpps_dT[i*poolSize:min(len(serpps_dT),(1+i)*poolSize)]
	avg_ = np.average(dataTest)
	stdDev_ = np.std(dataTest)
	poolAvg.append(avg_)
	poolStdDev.append(stdDev_)
	poolCentre.append((i+0.5)*poolSize)
	
groupBound = [0]		# stores boundary between sets of data
groupAvg = []		# stores average of data bounded by groupBound
groupStdDev = []		# stores standard deviation of data bounded by groupBound

for i in range(len(poolCentre)-1):
	if (abs(poolAvg[1+i]-poolAvg[i])>poolStdDev[1+i]+poolStdDev[i]):
		groupBound.append((i+1)*poolSize)
		groupAvg.append(np.average(serpps_dT[groupBound[-2]:groupBound[-1]]))
		groupStdDev.append(np.std(serpps_dT[groupBound[-2]:groupBound[-1]]))
		
groupCentre = [0]*(len(groupBound)-1)
for i in range(len(groupCentre)):
	groupCentre[i] = (groupBound[i]+groupBound[1+i])/2
		

serser_dT = [0]*(len(ser_T)-1)
ppspps_dT = [0]*(len(ser_T)-1)
o_n = 100
serser_ndT = [0]*(len(ser_T)-o_n)
for i in range(len(ser_T)-1):
	serser_dT[i] = ser_T[1+i]-ser_T[i]
	ppspps_dT[i] = pps_T[1+i]-pps_T[i]
for i in range(len(serser_ndT)):
	serser_ndT[i] = ser_T[o_n+i]-ser_T[i]
	
plotThresh = 1000	
	
for dat_i in range(len(groupCentre)):
	if (groupBound[dat_i+1]-groupBound[dat_i]<plotThresh):
		continue
	histData = serpps_dT[groupBound[dat_i]:groupBound[dat_i+1]]
	
	binNum = 1000
	varAllow = 1000
	binMin = 0
	binMax = 1000
	
	binWidth = (binMax - binMin)
	binEdges = np.linspace(binMin, binMax, binNum)
	
	binVals = np.histogram(histData, bins=binEdges)[0]
	
	binMids = [0]*len(binVals)
	
	for i in range(len(binMids)):
		binMids[i] = (binEdges[i]+binEdges[1+i])/2.0
	
	plt.plot(binMids, binVals)
	plt.title("Ser_PPS dist for datapoints "+str(groupBound[dat_i])+", "+str(groupBound[dat_i+1]))
	plt.xlabel("Ser PPS dt")
	plt.ylabel("Frequency")
	plt.savefig(filename+str(groupBound[dat_i])+","+str(groupBound[dat_i+1]), dpi=1000)
	plt.cla()		