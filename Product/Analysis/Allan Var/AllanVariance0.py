"""
Created on Thu Mar 31 17:33:12 2016

@author: Duncan

plot Allan var

input format:
...
<ser_time>,<pps_time>,<est_time>,...
...

doesn't matter which other lines are present; information extracted from t<><> row

"""
import numpy as np
import matplotlib as mplt
import matplotlib.pyplot as plt
import math as mth

filename = "KL1PRD09ChkCor"	

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

start = 0
end = "end"

def AllanAvg(data, order):
	tot = 0
	for i in range(len(data)-order):
		tot += data[order+i]-data[i]
	tot /= (order*(len(data)-order))
	return tot
	
def AllanVar(data, order):
	tot = 0
	num = int(len(data)/order)
	for i in range(num-2):
		term = (data[order*(i+2)]-2*data[order*(i+1)]+data[order*(i)])
		tot += (term)**2
	tot /= ((num-2)*2*((1000*order)**2))
	return tot
 
def GetDifferences(data):
	data_d = [data[i+1]-data[i] for i in range(len(data)-1)]
	return data_d	
	

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

alMin = 1
alMax = len(dataCol[0])/8
alFac = 1.3
alNum = int(round(mth.log(alMax/alMin,alFac)))

allan_x = [int(alMin*(alFac**i)) for i in range(alNum+1)]

ppspps_Allan = allan_x[:]
serser_Allan = allan_x[:]
k1ek1e_Allan = allan_x[:]
ppsser_Allan = allan_x[:]
ppsk1e_Allan = allan_x[:]
pps_Allan = allan_x[:]
ser_Allan = allan_x[:]

ppspps_dT = GetDifferences(dataCol[oset_pps])
serser_dT = GetDifferences(dataCol[oset_ser])
k1ek1e_dT = GetDifferences(dataCol[oset_est])
ppsser_dT = [dataCol[oset_ser][i]-dataCol[oset_pps][i] for i in range(len(dataCol[0]))]
ppsk1e_dT = [dataCol[oset_est][i]-dataCol[oset_pps][i] for i in range(len(dataCol[0]))]

for i in range(len(allan_x)):
	ppspps_Allan[i] = (AllanVar(ppspps_dT, allan_x[i])**0.5)
	serser_Allan[i] = (AllanVar(serser_dT, allan_x[i])**0.5)
	k1ek1e_Allan[i] = (AllanVar(k1ek1e_dT, allan_x[i])**0.5)
	ppsser_Allan[i] = (AllanVar(ppsser_dT, allan_x[i])**0.5)
	ppsk1e_Allan[i] = (AllanVar(ppsk1e_dT, allan_x[i])**0.5)
	pps_Allan[i] = (AllanVar(dataCol[oset_pps], allan_x[i])**0.5)
	ser_Allan[i] = (AllanVar(dataCol[oset_ser], allan_x[i])**0.5)
	


pltDat = [ ppspps_Allan , serser_Allan , k1ek1e_Allan , ppsser_Allan , ppsk1e_Allan , pps_Allan , ser_Allan]
savDat = ["ppspps_Allan","serser_Allan","k1ek1e_Allan","ppsser_Allan","ppsk1e_Allan","pps_Allan","ser_Allan"]
titDat = ["PPS-PPS"     ,"Serial-serial","Kalman-Kalman","PPS-serial","PPS-Kalman","PPS","Serial"]

#allan_x = [i for i in range(1,int(len(dataCol[0])/4),3)]
#
#sin_t = [i*10 + np.sin(i/100) for i in range(len(dataCol[0]))]
#
#for i in range(len(sin_t)):
#	sin_t[i] += (np.random.uniform(0.0,1.0)-0.5)*0.0
#	
#plt.plot(sin_t)
#plt.show()
#sin_dt = GetDifferences(sin_t)
#plt.plot(sin_dt)
#plt.show()
#
#sinsin_Allan = allan_x[:]
#for i in range(len(allan_x)):
#	sinsin_Allan[i] = (AllanVar(sin_dt, allan_x[i])**0.5)
#pltDat = [sinsin_Allan]
#
#savDat = ["a"]
#titDat = ["sin"]

mplt.rcParams.update({'font.size': 14})
for i in range(len(pltDat)):
	
	for k in range(1,2,1):		# start from 0 to plot non-log
	
		data = pltDat[i]
		name = savDat[i]
		title = titDat[i]
		datax = allan_x
				
		print(title, "min", min(data), data.index(min(data)), "max", max(data), data.index(max(data)))
		
		fig = plt.figure(figsize=(11,6))
		y_formatter = mplt.ticker.ScalarFormatter(useOffset=False)
		axes = plt.axes()
			
		plt.plot(allan_x,data, color="k")
		plt.title("Allan deviation of "+title)
		plt.xlabel("Order")
		plt.ylabel("Allan deviation / fractional")
		
		if (k==0):
			# find a measure of spread of data
			# find order of range
			dataRange = max(data)-min(data)
			order = 1
			while(order>dataRange):
				order/=10
			while(order<dataRange):
				order*=10
			if (order>1):	order/=10
			order/=10
				
			plt.ylim(int(min(data)/order-1)*order, int(max(data)/order+1)*order)
			axes = plt.axes()
			axes.yaxis.set_major_formatter(y_formatter)
		else:
			plt.yscale('log')
			plt.xscale('log')
				
		saveFileNameLog = ""
		if (k==1):	saveFileNameLog = "Log"
		saveFileName = filename+"_"+name+saveFileNameLog+"("+str(start)+"-"+str(end)+")"
		plt.savefig("../../Results/"+saveFileName+".png", dpi=400)
		plt.savefig("../../Results/"+saveFileName+".svg")
		plt.show()