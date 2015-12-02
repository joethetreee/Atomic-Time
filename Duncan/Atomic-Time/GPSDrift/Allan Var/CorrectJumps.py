import time
import numpy as np
import matplotlib.pyplot as plt
filename = "PPSSer12"

contents = open(filename+".txt", mode='r')
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


contents = open(filename+"Cor.txt", mode='a')		# open/create file to write
for i in range(len(ser_T)):
	contents.write(str(ser_T[i])+","+str(pps_T[i])+"\n")
contents.close()