import time
import numpy as np
import matplotlib.pyplot as plt
#from decimal import *
#getcontext().prec = 18

"""
removes jumps caused by loss of GPS fix
input and output format:
<ser_time>,<pps_time>,<est_time>,<sat_num>

<> are not present and are there only to clarify data names

Problem: after long PPS freezes/disconnect fixes there is sometimes a shift in PPS-ser times
this could be caused by avgPPS not being correct at that time
"""

filename = "KL1PRD12Chk"



parts = 4
oset_ser = 0 			# offset line for serial timing
oset_pps = 1 			# offset line for PPS data
oset_est = 2 			# offset line for PPS estimate
oset_sat = 3 			# offset line for satellite number

period = 1 				# number of lines for each second of data (will be computed)

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

def CheckLineStart(text, textStart):
	if (len(text)>=len(textStart)):
		if (text[:len(textStart)]==textStart):
			return True
	return False

def ConvertHHMMSS_s(tH):
	ts = int(tH[:2])*60*60
	ts += int(tH[2:4])*60
	ts += int(tH[4:6])
	return ts


# remove data without a fix
#contentsTxt = contentsTxt[24000:30000]
contentsTxtCor = [0]*len(contentsTxt)
i = 0
j = 0
delete = False 					 	# whether we must delete the current entry
serPrev = 0 							# previous serial time
ppsPrev = 0							# previous pps time
while (i<len(contentsTxt)-period+1):
	line = contentsTxt[i]
	data = [0]*parts
	commaLoc,commaLoc2 = 0,0
	for col in range(parts):
		if (col==parts-1):
			commaLoc2 = len(line)
		else:
			commaLoc2 = commaLoc+line[commaLoc:].index(',')
		try:	data[col] = int(line[commaLoc:commaLoc2])
		except ValueError:	data[col] = float(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1
			
	if (not delete): 		# check if the conctn is new -- check & remove new conctn data where the is no new pps since
		# check if there was a pps signal since the previous msg (which had no connection), or for partial soverflows
		if (abs(data[oset_ser]-data[oset_pps])>1000 or abs(data[oset_ser]-data[oset_est])>1000):
			delete = True
			print("too big", data)
		elif (j>0 and round(data[oset_pps]-ppsPrev)==0):
			print(ppsPrev, data[oset_pps])
			delete = True
	
	if (delete):
		i += period
		delete = False
		print("delete", line,"  ;",i)
	else:
		ppsPrev = data[oset_pps]
		for k in range(period):
			#print(line,"  ;",i,j)
			contentsTxtCor[j] = line
			j += 1
			i += 1

# truncate array to the end of the data		
contentsTxtCor = contentsTxtCor[:j]



ppsAvg = 1000

# detect and remove jumps
	
# work out jumps in time from GGA message
ppsCur = 0 								# time of PPS for current line
ppsPrev = 0 							# time of PPS for previous line
serCur = 0 							 	# time of serial for previous line
serPrev = 0 							# time of serial for previous line
estCur = 0
estPrev = 0
ppsCorrection = 0.


dataRow = [[0]*parts for i in range(len(contentsTxtCor))]

for row in range(len(dataRow)):
	line = contentsTxtCor[row]
	commaLoc,commaLoc2 = 0,0
	for col in range(parts):
		if (col==parts-1):
			commaLoc2 = len(line)
		else:
			commaLoc2 = commaLoc+line[commaLoc:].index(',')
		try:	dataRow[row][col] = int(line[commaLoc:commaLoc2])
		except ValueError:	dataRow[row][col] = float(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1
		
dataCol = [[0]*len(dataRow) for i in range(parts)]

pps_dt_dist_ = [dataRow[row+1][oset_pps]-dataRow[row][oset_pps] for row in range(len(dataRow)-1)]
pps_dt_dist = []
for row in range(len(pps_dt_dist_)):
	if (round(pps_dt_dist_[row],-1) == 1000):
		pps_dt_dist.append(pps_dt_dist_[row])
pps_dt_dist.sort()
		
def GetRandSec(iAnchor, iStd = 20):
	iAnchor = int(round(iAnchor))
	rand_i = -1
	rand_sec = 0
	j = 0
	while(rand_i<0 or rand_i>=len(pps_dt_dist) or round(rand_sec,-1)!=1000):
		if (j>10):						# if we have tried and failed too many times with full array
			rand_i = np.random.randint(0, len(pps_dt_dist))
			if (rand_i>=0 and rand_i<len(pps_dt_dist)):
				rand_sec = pps_dt_dist[rand_i]
		else:
			rand_i = int(round(np.random.normal(iAnchor, iStd)))
			if (rand_i>=0 and rand_i<len(pps_dt_dist)):
				rand_sec = pps_dt_dist_[rand_i]
		j += 1
	return rand_sec
				
followup = False
ppsCorCommon = 0
for i in range(len(dataRow)):
	
	ppsPrev = ppsCur
	serPrev = serCur
	estPrev = estCur
	
	data = dataRow[i]
	ppsCur = data[oset_pps]
	serCur = data[oset_ser]
	estCur = data[oset_est]
	
	if (i==0): 							 	# go back to start of loop if i is 0 (need to take diff between successive data)
		print("__ ~ __")
		continue
		
	pps_dt = ppsCur-ppsPrev
	ser_dt = serCur-serPrev
	est_dt = estCur-estPrev
	
	ppsser_dt = serCur-ppsCur
	ppsser_mil = int(round(ppsser_dt/1000))*1000 		 	# get difference rounded to nearest thousand
	ppsest_dt = estCur-ppsCur
	ppsest_mil = int(round(ppsest_dt/1000))*1000 	# get difference rounded to nearest thousand
	
	if (followup):
		print(ppsPrev, ppsCur," ", pps_dt, ppsCorrection," ", pps_dt-ppsCorrection)
	if (int(round(pps_dt-ppsCorrection,0))==0000):
		ppsCorrection += ppsCorCommon
		print("carry through")
		if (followup):
			print(pps_dt, ppsCorrection," ", pps_dt-ppsCorrection)
	followup = False
	if (int(round(pps_dt-ppsCorrection,-3))!=1000):
		ppsCorCommon = (pps_dt-1000)
		ppsCorrection = ppsCorCommon
		ppsCorrection = pps_dt-GetRandSec(i)				# if inaccurate, reset second length to 1000
		followup = True
	
	ppsCur -= ppsCorrection
	if (followup):
		print("->followup", ppsPrev, ppsCur, pps_dt, ppsCorrection)
	serCur = ppsCur + ppsser_dt - ppsest_mil
	estCur = ppsCur + ppsest_dt - ppsest_mil
			
	dataNew = data[:]
		
	dataNew[oset_ser] = serCur
	dataNew[oset_pps] = ppsCur
	dataNew[oset_est] = estCur
	
	contentsTxtCor[i] = ""
	for commaNum in range(0,4):
		if (type(data[commaNum])==int):
			contentsTxtCor[i] += str(int(round(dataNew[commaNum])))+","
		else:
			contentsTxtCor[i] += str(round(dataNew[commaNum],3))+","
	contentsTxtCor[i] = contentsTxtCor[i][:-1]+"\n"


contents = open("../../Results/"+filename+"Cor.txt", mode='w')		# open/create file to write

for i in range(len(contentsTxtCor)):
	line = str(contentsTxtCor[i])
	if (i==len(contentsTxtCor)-1):
		line = line[:-1]
	contents.write(line)
	
contents.close()