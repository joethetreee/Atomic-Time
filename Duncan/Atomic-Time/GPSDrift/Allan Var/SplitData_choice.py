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

boundL = 5400
boundH = 9600

ser_T = ser_T[boundL:boundH]
pps_T = pps_T[boundL:boundH]

serpps_dT = [0]*(len(ser_T))

for i in range(len(ser_T)):
	serpps_dT[i] = ser_T[i]-pps_T[i]

histData = serpps_dT

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
plt.title("Ser_PPS dist for datapoints "+str(boundL)+", "+str(boundH))
plt.xlabel("Ser PPS dt")
plt.ylabel("Frequency")
plt.savefig("DataSplit_Choice\\"+filename+"_dist_"+str(boundL)+","+str(boundH), dpi=1000)