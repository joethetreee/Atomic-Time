import time
import numpy as np
import matplotlib.pyplot as plt

"""
removes jumps caused by loss of GPS fix
input and output format:
$GPGGA...
$GPSMC...
t<ser_time>,<pps_time>

<> are not present and are there only to clarify data names

Problem: after long PPS freezes/disconnect fixes there is sometimes a shift in PPS-ser times
this could be caused by avgPPS not being correct at that time
"""

filename = "GPSMIL37Chckd"


oset_GGA = 0 			# offset line for GGA
oset_PPS = 2 			# offset line for PPS line

period = 3 				# number of lines for each second of data (will be computed)

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


# Calculate period
period = 1
while (CheckLineStart(contentsTxt[oset_GGA+period],"$GPGGA")==False):
	period += 1

print(period)

# remove data without a fix
#contentsTxt = contentsTxt[40002:50001]
contentsTxtCor = [0]*len(contentsTxt)
i = 0
j = 0
conPrev = False 						# whether the previous dataset had a connection
delete = False 					 	# whether we must delete the current entry
ser_Prev = 0 							# previous serial time
pps_Prev = 0							# previous pps time
while (i<len(contentsTxt)-period+1):	 		 	# while loop because for loop does not work as in C/C++ when modifying iterator in-loop!!!
	print (i)
	print (contentsTxt[i+oset_GGA])
	if (CheckLineStart(contentsTxt[i+oset_GGA],"$GPGGA")==True):
		commaLoc = 0
		for commaNum in range(6): 	 	# find quality value (fix/no fix)
			commaLoc += contentsTxt[i+oset_GGA][commaLoc:].index(',')+1
		commaLoc2 = commaLoc+contentsTxt[i+oset_GGA][commaLoc:].index(',')
		qVal = int(contentsTxt[i+oset_GGA][commaLoc:commaLoc2])
		if (qVal == 0):
			print("qVal", i, contentsTxt[i+oset_GGA])
			delete = True
	if (CheckLineStart(contentsTxt[i+oset_PPS],"t")==True):
		commaLoc = contentsTxt[i+oset_PPS].index(',')
		ser_t = int(contentsTxt[i+oset_PPS][1:commaLoc])
		pps_t = int(contentsTxt[i+oset_PPS][commaLoc+1:])
		
		if (pps_t == 0):
			print("pps_t", i, contentsTxt[i+oset_PPS])
			delete = True
		elif (pps_t == pps_Prev):
			print("pps_t", i, contentsTxt[i+oset_PPS])
			delete = True
		elif (ser_t == ser_Prev):
			print("ser_t", i, contentsTxt[i+oset_PPS])
			delete = True
		ser_Prev = ser_t
		pps_Prev = pps_t
	
	if (not delete and not conPrev): 		# check if the conctn is new -- check & remove new conctn data where the is no new pps since
		commaLoc = 1+contentsTxt[i+oset_PPS][1:].index(",")
		#print("~",contentsTxt[i+oset_PPS][1:commaLoc])
		ser_t = int(contentsTxt[i+oset_PPS][1:commaLoc])
		pps_t = int(contentsTxt[i+oset_PPS][commaLoc+1:])
		if (ser_t-pps_t>1000): 		# check if there was a pps signal since the previous msg (which had no connection)
			delete = True
	
	if (delete):
		i += period
		delete = False
		conPrev = False
	else:
		for k in range(period):
			contentsTxtCor[j] = contentsTxt[i]
			j += 1
			i += 1
			conPrev = True

# truncate array to the end of the data		
contentsTxtCor = contentsTxtCor[:j]

contents = open(filename+"Fix.txt", mode='w')		# open/create file to write

for i in range(len(contentsTxtCor)):
	contents.write(str(contentsTxtCor[i]))
	
contents.close()


# find average pps time length by finding first and last time
# find first measurement value
ni = 0 							# find measurement number for first measurement (numbered using GPS time/s)
ti = 0 							# find time for first measurement (using pps time /ms)
j = 0

commaLoc = 0
for commaNum in range(1): 	 	 	 	# find time in HHMMSS corresponding to first measurement with fix
	commaLoc += contentsTxtCor[oset_GGA][commaLoc:].index(',')+1
ni = str(contentsTxtCor[oset_GGA][commaLoc:commaLoc+6])

# find first time
commaLoc = 0
for commaNum in range(1): 	 	# find time
	commaLoc += contentsTxtCor[oset_PPS][commaLoc:].index(',')+1
ti = int(contentsTxtCor[oset_PPS][commaLoc:])

# find last measurement value
nf = 0 							# find measurement number for last measurement (numbered using GPS time/s)
tf = 0 							# find time for last measurement (using pps time /ms)

commaLoc = 0
for commaNum in range(1): 	 	# find time
	commaLoc += contentsTxtCor[len(contentsTxtCor)-period+oset_GGA][commaLoc:].index(',')+1
nf = str(contentsTxtCor[len(contentsTxtCor)-period+oset_GGA][commaLoc:commaLoc+6])

# find last time
commaLoc = 0
for commaNum in range(1): 	 	# find time
	commaLoc += contentsTxtCor[len(contentsTxtCor)-period+oset_PPS][commaLoc:].index(',')+1
tf = int(contentsTxtCor[len(contentsTxtCor)-period+oset_PPS][commaLoc:])

print(tf,ti)	
# find difference in time
nif = ConvertHHMMSS_s(nf)-ConvertHHMMSS_s(ni)
if (nif<0):
	nif += 60*60*24
	
	
#ppsAvg = (tf-ti) / nif
ppsAvg = 1000

print ("ti, tf, ni, nf, nif, ppsAvg",ti, tf, ni, nf, nif, ppsAvg)

# detect and remove jumps
	
# work out jumps in time from GGA message
ppsCur = 0 								# time of PPS for current line
ppsPrev = 0 							# time of PPS for previous line
serCur = 0 							 	# time of serial for previous line
serPrev = 0 							# time of serial for previous line
ggaCur = 0 								# time of GGA for current line
ggaPrev = 0 							# time of GGA for previous line
for i in range(0, len(contentsTxtCor)-1, period):
	#print("->i:",i)	
	
	ggaPrev = ggaCur
	ppsPrev = ppsCur
	serPrev = serCur
	
	# find absolute time using GGA
	line = contentsTxtCor[oset_GGA+i]
	commaLoc = 0
	for commaNum in range(1): 	 	# find time
		#print("A",oset_GGA+i)
		commaLoc += line[commaLoc:].index(',')+1
	ggaH = line[commaLoc:commaLoc+6] 			# GGA time in HHMMSS format (string)
	ggaCur = ConvertHHMMSS_s(ggaH)
	
	# find pps using pps data
	line = contentsTxtCor[oset_PPS+i]
	commaLoc = 0
	for commaNum in range(1): 	 	# find time
		#print("B",oset_PPS+i)
		commaLoc += line[commaLoc:].index(',')+1
	serCur = int(line[1:commaLoc-1])
	ppsCur = int(line[commaLoc:])
	
	if (i==0): 							 	# go back to start of loop if i is 0 (need to take diff between successive data)
		continue
	
	ggad = ggaCur-ggaPrev 						# difference in seconds between messages
	if (ggad<0):
		ggad += 60*60*24
		
	pps_dt = int(ppsCur-ppsPrev)
	ser_dt = int(serCur-serPrev)
	
	ppsser_dt = serCur-ppsCur
	ppsser_mil = int(ppsser_dt/1000)*1000 		# get difference rounded to nearest thousand

	#print("->",i,ppsCur,serCur,  "dt",pps_dt,ser_dt,ppsser_dt,ppsser_mil)
	
	ppsCur += int(int(1-round(pps_dt,-3)/1000)*ppsAvg)		# correct by however much the pps difference varies from 1000
	serCur = ppsCur + ppsser_dt - ppsser_mil
	
	#print(ppsCur,serCur)
		
	#print("ggad: ",ggad)
	#print("dt_pps: ",dt_pps)
	
	contentsTxtCor[oset_PPS+i] = "t"+str(serCur)+","+str(ppsCur)+"\n"


contents = open("../../Results/"+filename+"Cor.txt", mode='w')		# open/create file to write

for i in range(len(contentsTxtCor)):
	contents.write(str(contentsTxtCor[i]))
	
contents.close()