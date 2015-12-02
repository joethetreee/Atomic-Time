# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 15:26:51 2015

@author: Duncan

plots distribution of difference between GPS data stream and the second
format: "tick length,connection fix\n"
"""
import numpy as np
import matplotlib.pyplot as plt

filename = "231312 18102015 GPSDrift_measurements.txt"
cumulative = True

colArray = ['red', 'blue', 'green', 'orange', 'purple']

file = open(filename, "r")
lines = file.read().split('\n')
dataChunk = [[0 for i in range(2)] for j in range(len(lines))]

offset=0		# keeps tracks of rows being deleted
for i in range(len(lines)):
	# split data into lines
	# check whether the line is formatted correctly (could have errors for last line)
	if ('\t' in lines[i]):
		dataString = lines[i].split("\t")
		dataChunk[i-offset][0] = int(dataString[0])
		dataChunk[i-offset][1] = int(dataString[1])
	else:
		print("delete ",i)
		dataChunk = dataChunk[:i]+dataChunk[i+1:]
		#np.delete(dataChunk,(i),axis=0)
		offset+=1
	
# split data up by value of column (whether GPS is connected)
valFix = []							# stores every value in the GPS connection column
valFix.append(dataChunk[0][1])		# enter first value to the list

# get every different GPS connection value
for i in range(len(dataChunk)):
	for j in range(len(valFix)):
		valSeenBefore=False
		if (dataChunk[i][1]==valFix[j]):	# check whether the value is already in array
			valSeenBefore=True
			break
	if (valSeenBefore==False):			# if value wasn't in array...
		valFix.append(dataChunk[i][1])	# add value to array
	
# deal with cumulative plot
# compute average
avg = 0.0
for i in range(len(dataChunk)):
	avg += dataChunk[i][0]
avg=(avg)/(len(dataChunk))

print (avg)
	
# split each row based on value for GPS connection -- these arrays will be plotted
t_a = [[] for i in range(len(valFix))]
t_g = [[] for i in range(len(valFix))]
	
if (cumulative):
	t_dif=0			# keeps track of current difference
	for i in range(len(dataChunk)):
		t_dif += dataChunk[i][0]-avg
		t_a[valFix.index(dataChunk[i][1])].append(t_dif)
		t_g[valFix.index(dataChunk[i][1])].append(i)
		
else:
	for i in range(len(dataChunk)):
		t_a[valFix.index(dataChunk[i][1])].append(dataChunk[i][0])
		t_g[valFix.index(dataChunk[i][1])].append(i)	

# sort out binValues

binMin = min(t_a[0])
binMax = max(t_a[0])

for fix in range(len(valFix)):
	binMin = min(binMin, min(t_a[fix]))
	binMax = max(binMax, max(t_a[fix]))


binRes = 4
binValues = [[] for i in range(len(valFix))]
binNumber = [[] for i in range(len(valFix))]
for fix in range(len(valFix)):
	binValues[fix]=np.linspace(binMin, binMax, (binMax-binMin)/binRes)
	
	
# sort data into bins
for fix in range(len(valFix)):
	binNumber[fix] = np.histogram(t_a[fix], bins=binValues[fix])[0]

# average bins
for fix in range(len(valFix)):
	for i in range(len(binValues[fix])-1):
		binValues[fix][i]=(binValues[fix][i]+binValues[fix][i+1])/2
	binValues[fix]=binValues[fix][:-1]
	
print(max(binNumber[1]))
	
print("sizes: ", len(binValues[0]), len(binNumber[0]))

fig = plt.figure()
ax1 = fig.add_subplot(111)

series=[0 for i in range(len(valFix))]
seriesTxt=["" for fix in range(len(valFix))]
for fix in range(len(valFix)):
	series[fix], = ax1.plot(binValues[fix], binNumber[fix], color=colArray[fix])
	seriesTxt[fix]=str(fix)
	
plt.xlabel("abs GPS time variation /ms")
plt.ylabel("frequency")
plt.legend(series,seriesTxt)
	
plt.show()