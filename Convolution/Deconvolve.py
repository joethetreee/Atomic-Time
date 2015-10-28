import time
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy
import scipy.signal

signal = open("T0001CH1_triggerSerial.csv", 'r')
signalData = []

dt = 1 / 125000

ppsPulse = np.zeros(125000)

k = 0
signalMax = 0
signalMaxPos = 0

filter = [0.6] * 12500

print("Reading signal waveform...")

for line in signal:
	temp = float(line.split(",")[1].rstrip("\n"))
	if temp > signalMax:
		signalMax = temp
		signalMaxPos = k
	signalData.append(temp)
	k += 1
	
print("Generating filter waveform...")
	
for i in range(0, 125000):
	if i >= signalMaxPos - 6250 and i < signalMaxPos + 6250:
		ppsPulse[i] = 0.6
	else:
		ppsPulse[i] = 0
		
print("Doing deconvolution...")
deconv = scipy.signal.deconvolve(signalData, filter)

plt.plot(range(len(signalData)), signalData)
plt.plot(range(len(signalData)), ppsPulse)
plt.plot(range(len(deconv[0])), deconv[0])
plt.show()