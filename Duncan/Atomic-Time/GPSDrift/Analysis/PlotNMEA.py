# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:26:51 2015

@author: Duncan

Reads NMEA GPS data. Picks out GGA sentences and plots the accuracy of each second
GGA lines should have additional argument (Arduino time between sentences, ms) after comma
sentences separated by \n (new line)
"""
import numpy as np
import matplotlib.pyplot as plt
import pynmea2

filename = "GPSLOG28.txt"
cumulative = True

colArray = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

file = open(filename, "r")
lines = file.read().split('\n')				# split lines by \n

print("length: ", len(lines))

# find GGA lines and sort into arrays for GGA lines and times

linesGGA=[]
timeD=[]								# Delta time (length of GPS second)

for i in range(len(lines)):
	if (len(lines[i])>(6+14)):			# check whether line is long enough
		if (lines[i][:6]=="$GPGGA"):	# check that the format is GPGGA
			contents=lines[i]			# want to remove the additional time to get into GGA
			commaLoc=-1					# store location of commas (want to find last entry)
			while (',' in contents[max(0,commaLoc)+1:]):	# check whether there is another comma
				commaLoc=contents.index(',',max(0,commaLoc)+1)
			linesGGA.append(pynmea2.parse(contents[:commaLoc]))
			timeD.append(int(contents[commaLoc+1:]))
			
timeAvg = sum(timeD)/len(timeD)
print (timeAvg)

timeV=[0 for i in range(len(linesGGA))]			# Variation in absolute time (since start) according to GPS
												# uses avg. GPS second as time unit
qCon=[0 for i in range(len(linesGGA))]			# quality of connection

for i in range(len(linesGGA)):					# get information for timeV and qCon
	qCon[i]=linesGGA[i].gps_qual
	if (i>0):
		timeV[i]=timeD[i]+timeV[i-1]-timeAvg
	else:
		timeV[0]=timeD[0]-timeAvg
		
plt.plot([i for i in range(len(qCon))], timeV)
plt.title("Variation in arrival time of GPS data (Calculated mean of "+str(timeAvg)+")")
plt.xlabel("Arduino time /s")
plt.ylabel("abs GPS time variation /ms")
	
plt.show()
			

#dataChunk = [[0 for i in range(2)] for j in range(len(lines))]
#
#offset=0		# keeps tracks of rows being deleted
#for i in range(len(lines)):
#	# split data into lines
#	# check whether the line is formatted correctly (could have errors for last line)
#	if ('\t' in lines[i]):
#		dataString = lines[i].split("\t")
#		dataChunk[i-offset][0] = int(dataString[0])
#		dataChunk[i-offset][1] = int(dataString[1])
#	else:
#		dataChunk = dataChunk[:i]+dataChunk[i+1:]
#		#np.delete(dataChunk,(i),axis=0)
#		offset+=1
#		print(i)
#	
## split data up by value of column (whether GPS is connected)
#valFix = []							# stores every value in the GPS connection column
#valFix.append(dataChunk[0][1])		# enter first value to the list
#
## get every different GPS connection value
#for i in range(len(dataChunk)):
#	for j in range(len(valFix)):
#		valSeenBefore=False
#		if (dataChunk[i][1]==valFix[j]):	# check whether the value is already in array
#			valSeenBefore=True
#			break
#	if (valSeenBefore==False):			# if value wasn't in array...
#		valFix.append(dataChunk[i][1])	# add value to array
#	
## deal with cumulative plot
## compute average
#avg = 0.0
#for i in range(len(dataChunk)):
#	avg += dataChunk[i][0]
#avg=(avg)/(len(dataChunk))
#
#print (avg)
#	
## split each row based on value for GPS connection -- these arrays will be plotted
#t_a = [[] for i in range(len(valFix))]
#t_g = [[] for i in range(len(valFix))]
#	
#if (cumulative):
#	t_dif=0			# keeps track of current difference
#	for i in range(len(dataChunk)):
#		t_dif += dataChunk[i][0]-avg
#		t_a[valFix.index(dataChunk[i][1])].append(t_dif)
#		t_g[valFix.index(dataChunk[i][1])].append(i)
#		
#else:
#	for i in range(len(dataChunk)):
#		t_a[valFix.index(dataChunk[i][1])].append(dataChunk[i][0])
#		t_g[valFix.index(dataChunk[i][1])].append(i)	
#		
#		
#
#fig = plt.figure()
#ax1 = fig.add_subplot(111)
#
#series=[0 for i in range(len(valFix))]
#seriesTxt=["" for i in range(len(valFix))]
#for i in range(len(valFix)):
#	series[i] = ax1.scatter(t_g[i], t_a[i], color=colArray[i])
#	seriesTxt[i]=str(i)	
#	
#plt.xlabel("Arduino time /s")
#plt.ylabel("abs GPS time variation /ms")
#plt.legend(series,seriesTxt)
#	
#plt.show()