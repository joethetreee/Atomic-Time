import time
import numpy as np
import matplotlib.pyplot as plt

"""
removes jumps caused by loss of GPS fix
input and output format:
<ser_time>,<pps_time>,<est_time>,<sat_num>

<> are not present and are there only to clarify data names

Problem: after long PPS freezes/disconnect fixes there is sometimes a shift in PPS-ser times
this could be caused by avgPPS not being correct at that time
"""

filename = "KL1PRD05Chk"


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
ser_Prev = 0 							# previous serial time
pps_Prev = 0							# previous pps time
while (i<len(contentsTxt)-period+1):	 		 	# while loop because for loop does not work as in C/C++ when modifying iterator in-loop!!!
	print (i)
	line = contentsTxt[i]
	print (line)
	commaLoc = 0
	for k in range(0,4):
		if (k==3):
			commaLoc2 = len(line)
		else:
			try:
				commaLoc2 = commaLoc+line[commaLoc:].index(',')
			except IndexError:
				print("ValError",line,i)
				delete = True
				break
		val = line[commaLoc:commaLoc2]
		try:
			val = int(val)
		except ValueError:
			print("ValError",val)
			delete = True
			break
		
		ser_t,pps_t = 0,0
		
		if (k==oset_ser):
			ser_t = val
		elif (k==oset_pps):
			pps_t = val
			if (pps_t==0):			# starts out as being 0; if unchanged, no pps was detected
				delete = True
				break
		
		commaLoc = commaLoc2+1
			
	if (not delete): 		# check if the conctn is new -- check & remove new conctn data where the is no new pps since
		if (ser_t-pps_t>1000): 		# check if there was a pps signal since the previous msg (which had no connection)
			delete = True
	
	if (delete):
		i += period
		delete = False
		print("delete", line,"  ;",i)
	else:
		for k in range(period):
			print(line,"  ;",i,j)
			contentsTxtCor[j] = line
			j += 1
			i += 1

# truncate array to the end of the data		
contentsTxtCor = contentsTxtCor[:j]
#contentsTxtCor = contentsTxtCor[:21]


ppsAvg = 1000

# detect and remove jumps
	
# work out jumps in time from GGA message
ppsCur = 0 								# time of PPS for current line
ppsPrev = 0 							# time of PPS for previous line
serCur = 0 							 	# time of serial for previous line
serPrev = 0 							# time of serial for previous line
estCur = 0
estPrev = 0
ppsCorrection = 0
for i in range(0, len(contentsTxtCor), period):
	#print("->i:",i)	
	
	ppsPrev = ppsCur
	serPrev = serCur
	estPrev = estCur
	
	data = [0]*4
	
	line = contentsTxtCor[i]
	commaLoc = 0
	for commaNum in range(4): 	 	# find time
		#print("B",oset_PPS+i)
		if (commaNum == 3):
			commaLoc2 = len(line)
		else:
			commaLoc2 = commaLoc+line[commaLoc:].index(',')
		data[commaNum] = int(line[commaLoc:commaLoc2])
		commaLoc = commaLoc2+1
		
	ppsCur = int(data[oset_pps])
	serCur = int(data[oset_ser])
	estCur = int(data[oset_est])
	
	if (i==0): 							 	# go back to start of loop if i is 0 (need to take diff between successive data)
		continue
		
	pps_dt = int(ppsCur-ppsPrev)
	ser_dt = int(serCur-serPrev)
	est_dt = int(estCur-estPrev)
	
	ppsser_dt = serCur-ppsCur
	ppsser_mil = int(round(ppsser_dt/1000))*1000 		 	# get difference rounded to nearest thousand
	ppsest_dt = estCur-ppsCur
	ppsest_mil = int(round(ppsest_dt/1000))*1000 	# get difference rounded to nearest thousand

	#print("->",i,ppsCur,serCur,  "dt",pps_dt,ser_dt,ppsser_dt,ppsser_mil)
	
	#ppsCur += int(int(1-round(pps_dt,-3)/1000)*ppsAvg)		# correct by however much the pps difference varies from 1000
	
	if (int(round(pps_dt-ppsCorrection,-3))!=1000):
		ppsCorrection = (pps_dt-1000)
		print("ppsCor",pps_dt,i,"   ",ppsPrev,ppsCur,ppsCorrection)
#	else:
#		print("ppsOK ",pps_dt,i,"   ",ppsPrev,ppsCur,ppsCorrection)
	ppsCur -= ppsCorrection
	serCur = ppsCur + ppsser_dt - ppsser_mil
	estCur = ppsCur + ppsest_dt - ppsest_mil
	
	#print(ppsCur,serCur)
		
	#print("ggad: ",ggad)
	#print("dt_pps: ",dt_pps)
		
	data[oset_ser] = serCur
	data[oset_pps] = ppsCur
	data[oset_est] = estCur
	
	contentsTxtCor[i] = ""
	for commaNum in range(0,4):
		contentsTxtCor[i] += str(data[commaNum])+","
	contentsTxtCor[i] = contentsTxtCor[i][:-1]+"\n"


contents = open("../../Results/"+filename+"Cor.txt", mode='w')		# open/create file to write

for i in range(len(contentsTxtCor)):
	line = str(contentsTxtCor[i])
	if (i==len(contentsTxtCor)-1):
		line = line[:-1]
	contents.write(line)
	
contents.close()