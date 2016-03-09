import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
filename = "GARNMEA20160229_155510ChckdCor"

contents = open("../../Results/"+filename+".txt", mode='r')
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
 
 
ser_T = [0]*len(contentsTxt)	 	# store serial times
pps_T = [0]*len(contentsTxt)	 	# store pps times
print(len(contentsTxt))
# put data into arrays
j=0
for i in range(len(ser_T)):
	line = contentsTxt[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_T[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j]
pps_T = pps_T[:j]	

allan_x = [int(pow(1.7,i)) for i in range(1,20,1)]
	
allan_sery = [0]*len(allan_x)
	
allan_ppsy = [0]*len(allan_x)

for i in range(len(allan_x)):
	#print(i, allan_x[i])
	allan_sery[i] = ((AllanVar(ser_T, allan_x[i]))**0.5)

for i in range(len(allan_x)):
	#print(i, allan_x[i])
	allan_ppsy[i] = ((AllanVar(pps_T, allan_x[i]))**0.5)
	print(allan_ppsy[i],0.5/np.sqrt(allan_x[i]),"    ",allan_x[i])
	
ardError_y = [1]*len(allan_x)
for i in range(len(ardError_y)):
	ardError_y[i] = 1
	
print(len(pps_T))
print(np.log2(len(pps_T)))	
	
fig = plt.figure(figsize=(10,6))
mplt.rcParams.update({'font.size': 12})	
ax1 = fig.gca()
ax2 = fig.gca()
ser_allan_ser, = ax1.plot(np.log(allan_x), np.log(allan_sery))
ser_allan_pps, = ax1.plot(np.log(allan_x), np.log(allan_ppsy))
ser_ardErr, = ax2.plot(np.log(allan_x), np.log(ardError_y))

plt.title("Allan Deviation per second")
plt.xlabel("Order")
plt.ylabel("Deviation / ms")
plt.legend([ser_allan_ser, ser_allan_pps, ser_ardErr], ["Allan serial", "Allan PPS", "1 ms/s Ard"])

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