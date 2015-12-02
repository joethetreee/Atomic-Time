# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 17:57:27 2015

@author: Duncan

Compute distribution of Serial signal from GPS from average

Measurement of PPS (regular square wave) triggered from start of serial
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import bisect

filename = "isfread\combined_triggerSerial.csv"
pulseStart = 0.0

pulseLen = 0.1				# length of PPS (s)
timeA = np.zeros(0)			# data for averaged PPS
pulseAvg_t = np.zeros(0)	# average of PPS signal in time domain
serialAvg_t = np.zeros(0)	# data for averaged serial
pulseOutline_t = np.zeros(0)	# data for theoretical single pulse

window = np.blackman 		# windowing function used

# find number of rows

fileTemp = open(filename)
textTemp = fileTemp.read()
row_count = textTemp.count("\n")


# sort data into arrays

with open(filename, newline='\n') as csvfile:
	readFile = csv.reader(csvfile, delimiter=',', quotechar='|')
	timeA = np.zeros(row_count)
	pulseAvg_t = np.zeros(row_count)
	serialAvg_t = np.zeros(row_count)
	pulseOutline_t = np.zeros(row_count)
	i=0
	for row in readFile:
		timeA[i] = float(row[0])
		pulseAvg_t[i] = float(row[1])
		serialAvg_t[i] = float(row[2])
		if (abs(timeA[i]-(pulseStart+pulseLen/2))<pulseLen/2):
			pulseOutline_t[i] = 1
		else:
			pulseOutline_t[i] = 0
		i+=1
	
dt = (timeA[row_count-1]-timeA[0])/(row_count-1)

# smooth out pulse data

print("A")

smoothing = 0

pulseAvg_t_ = np.copy(pulseAvg_t)

for i in range(len(pulseAvg_t)):
	smoothingAct = min(smoothing, i, len(pulseAvg_t)-1-i)
	avg = 0
	smoothingAct = 2*smoothingAct+1
	for j in range(smoothingAct):
		avg += pulseAvg_t[i-int(smoothingAct/2)+j]
	avg /= smoothingAct
	pulseAvg_t[i] = avg
		
print("B")

# array for frequencies
df = 1.0/timeA[-1]
freqA = np.zeros(len(timeA))
for i in range(len(freqA)):
	freqA[i]=i*df


#pulseAvg_f = np.fft.fft(pulseAvg_t)
pulseAvg_f = np.fft.fft(pulseAvg_t)
#plt.plot(pulseAvg_f)

#pulseOutline_f = np.fft.fft(pulseOutline_t)
pulseOutline_f = np.fft.fft(pulseOutline_t*window(len(pulseOutline_t)))
#plt.plot(freqA[:100], pulseOutline_f[:100])

#serialAvg_f = np.fft.fft(serialAvg_t)
serialAvg_f = np.fft.fft(serialAvg_t)
#plt.plot(serialAvg_f)

print("C")

# create arrays for non-truncated data
pulseAvg_t3 = np.fft.ifft(pulseAvg_f)
pulseOutline_t3 = np.fft.ifft(pulseOutline_f)
dist_f = np.zeros(len(timeA), dtype=complex)

for i in range(len(dist_f)):
	if (pulseAvg_f[i]==0):
		dist_f[i] = 0
	else:
		dist_f[i] = pulseAvg_f[i]/pulseOutline_f[i]

# truncate to f=fHigh
fHigh = 1000
fIndex = min(len(freqA), bisect.bisect_left(freqA, fHigh))

pulseAvg_f = pulseAvg_f[:fHigh]
pulseOutline_f = pulseOutline_f[:fHigh]
serialAvg_f = serialAvg_f[:fHigh]
freqA2 = freqA[:fHigh]

for i in range(len(dist_f)):
	if (i>=fHigh):
		dist_f[i]=0
		
dist_t3 = np.fft.ifft(dist_f)

print("D")

# Inverse DFT to the time domain

dist_f2 = dist_f[:fHigh]
dist_t2 = np.fft.ifft(dist_f2)

pulseAvg_t2 = np.fft.ifft(pulseAvg_f)
pulseOutline_t2 = np.fft.ifft(pulseOutline_f)

# create new time array for truncated data
dt2 = 1/freqA2[-1]


timeA2 = np.zeros(len(freqA2))
for i in range(len(timeA2)):
	timeA2[i]=i*dt2

# normalise array
integral = sum(dist_t2)*dt2
dist_t2/=(integral/2)

integral = sum(pulseAvg_t2)*dt2
pulseAvg_t2/=(integral/2)

integral = sum(pulseAvg_t)*dt
pulseAvg_t/=integral

maxIndex = np.argmax(pulseOutline_t2)
integral = max(pulseOutline_t2[(maxIndex+(pulseLen/2)/dt2)%len(pulseOutline_t2)],
						pulseOutline_t2[(maxIndex-(pulseLen/2)/dt2)%len(pulseOutline_t2)])	
pulseOutline_t2*=1/(integral/2)

integral = sum(pulseAvg_t3)*dt
pulseAvg_t3/=integral

integral = sum(pulseOutline_t3)*dt
pulseOutline_t3/=integral

integral = sum(abs(dist_t3))*dt
dist_t3/=integral

print("E")

# check by doing convolution
reconstruction_t2 = np.zeros(len(timeA2), dtype=complex)
for i in range(len(reconstruction_t2)):
	contribution = dist_t2[i]					# get contribution from distribution
	for j in range(np.argmax(timeA2>pulseLen)):
		reconstruction_t2[(i+j)%len(reconstruction_t2)]+=contribution
integral = sum(reconstruction_t2)*dt2
reconstruction_t2/=(integral)

reconstruction_t3 = np.zeros(len(timeA), dtype=complex)
#spacing = 1
#for i in range(int(len(reconstruction_t3)/spacing)):
#	contribution = 0
#	for j in range(spacing):					# get contribution from distribution
#		contribution += dist_t3[i*spacing+j]
#	contribution /= spacing
#	for j in range(np.argmax(timeA>pulseLen)):
#		reconstruction_t3[(i*spacing+j)%len(reconstruction_t3)]+=contribution
integral = sum(reconstruction_t3)*dt
reconstruction_t3/=(integral)


print("F")

# plot
fig = plt.figure()
ax1 = fig.add_subplot(111)


series_PPSAvg, = ax1.plot(timeA, abs(pulseAvg_t))
series_Dist, = ax1.plot(timeA, abs(dist_t3))
series_Convolution, = ax1.plot(timeA2, abs(reconstruction_t2))
#plt.plot(freqA2, dist_f)


plt.title("Distribution of start of pulse, leading edge offset "+str(pulseStart)+" s")
plt.xlabel("time /s")
plt.ylabel("probability density")
plt.legend([series_PPSAvg, series_Dist, series_Convolution], 
					['Avg PPS', 'Prob dist of PPS leading edge', 'Reconstructed PPS (convolution)'])
			
plt.show()
					
print("G")