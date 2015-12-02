import numpy as np
import matplotlib.pyplot as plt
filename = "PPSSer12.txt"

contents = open(filename, mode='r')
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

serser_dT = [0]*(len(ser_T)-1)
ppspps_dT = [0]*(len(ser_T)-1)
serpps_dT = [0]*(len(ser_T))
o_n = 100
serser_ndT = [0]*(len(ser_T)-o_n)

for i in range(len(ser_T)):
	serpps_dT[i] = ser_T[i]-pps_T[i]
for i in range(len(ser_T)-1):
	serser_dT[i] = ser_T[1+i]-ser_T[i]
	ppspps_dT[i] = pps_T[1+i]-pps_T[i]
for i in range(len(serser_ndT)):
	serser_ndT[i] = ser_T[o_n+i]-ser_T[i]
	
histData = serpps_dT


# apply maximum filter
#minVal = 000
#maxVal = 2000
#j=0
#while(j<len(histData)):
#	if (histData[j]>maxVal):
#		histData = histData[:j]+histData[j+1:]
#	elif (histData[j]<minVal):
#		histData = histData[:j]+histData[j+1:]
#	else:
#		j += 1

binNum = 1000
varAllow = 1000
binMin = 0
binMax = 1000

print(binMin, binMax)

binWidth = (binMax - binMin)
binEdges = np.linspace(binMin, binMax, binNum)

binVals = np.histogram(histData, bins=binEdges)[0]

binMids = [0]*len(binVals)

for i in range(len(binMids)):
	binMids[i] = (binEdges[i]+binEdges[1+i])/2.0
	
	
fig = plt.figure()
ax = fig.gca()
plt.plot(binMids, binVals)
plt.xlim(binMin, binMax)
plt.title("PPS->Serial dt")
plt.xlabel("time / ms")
plt.ylabel("frequency")

plt.show()