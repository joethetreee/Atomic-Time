import time
import numpy as np
import matplotlib.pyplot as plt
filename = "PPSSer12.txt"

contents = open(filename, mode='r')
contentsTxt = contents.readlines()
contents.close()

def AllanAvg(data, order):
	tot = 0
	for i in range(len(data)-order):
		tot += data[order+i]-data[i]
	tot /= (order*(len(data)-order))
	return tot
	
def AllanVar(data, order):
	tot = 0
	allanAvg = AllanAvg(data, order)
	for i in range(len(data)-order):
		term = (data[order+i]-data[i])/order
		tot += (term-allanAvg)**2
	tot /= (len(data)-order)
	return tot

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
		
# remove any outliers due to jumps
dt_pps = 0						# correct by this amount
dt_ser = 0						# correct by this amount
serAvg = (ser_T[-1]-ser_T[0])/len(ser_T)
ppsAvg = (pps_T[-1]-pps_T[0])/len(ser_T)
print(pps_T[0],pps_T[1],pps_T[2])
for i in range(len(ser_T)-1):
	if (pps_T[1+i]-pps_T[i]>2000):
		dt_pps = int(ppsAvg-(pps_T[1+i]-pps_T[i]))
		dt_ser = int(serAvg-(ser_T[1+i]-ser_T[i]))
		print(dt_pps, dt_ser)
		for j in range(i+1, len(ser_T)):
			pps_T[j] += dt_pps
			ser_T[j] += dt_ser
		
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
	
	
allan_x = range(1, 200)
allan_y = [0]*len(allan_x)

for i in range(len(allan_x)):
	print(i)
	allan_y[i] = ((AllanVar(ser_T, allan_x[i]))**0.5)
	
ardError_y = [1]*len(allan_x)
for i in range(len(ardError_y)):
	ardError_y[i] = 1
	
fig = plt.figure()
ax1 = fig.gca()
ax2 = fig.gca()
ser_allan, = ax1.plot((allan_x), (allan_y))
ser_ardErr, = ax2.plot((allan_x), (ardError_y))

plt.title("Allan Deviation per second")
plt.xlabel("Order")
plt.ylabel("Deviation / ms")
plt.legend([ser_allan, ser_ardErr], ["Allan", "1 ms/s Ard"])

plt.show()

	
#histData = serser_ndT
#
#
## apply maximum filter
##minVal = 000
##maxVal = 2000
##j=0
##while(j<len(histData)):
##	if (histData[j]>maxVal):
##		histData = histData[:j]+histData[j+1:]
##	elif (histData[j]<minVal):
##		histData = histData[:j]+histData[j+1:]
##	else:
##		j += 1
#
#binNum = 1000
#varAllow = 1000
#binMin = 1000*o_n-varAllow
#binMax = 1000*o_n+varAllow
#
#print(binMin, binMax)
#
#binWidth = (binMax - binMin)
#binEdges = np.linspace(binMin, binMax, binNum)
#
#binVals = np.histogram(histData, bins=binEdges)[0]
#
#binMids = [0]*len(binVals)
#
#for i in range(len(binMids)):
#	binMids[i] = (binEdges[i]+binEdges[1+i])/2.0
#	
#	
#fig = plt.figure()
#ax = fig.gca()
#plt.plot(binMids, binVals)
#plt.xlim(binMin, binMax)#
#
#plt.show()