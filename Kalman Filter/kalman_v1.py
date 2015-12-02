import numpy as np
import matplotlib.pyplot as plt
import math
import time

file = open("PPSSER.csv", 'r')
serial = []
pps = []

arduinoSecond = 1001.26
arduinoUncertainty = 1
gpsUncertainty = 100

# Extract data from file
for line in file:
	split = line.split(",")
	serial.append(int(split[0]))
	pps.append(int(split[1]))
	
# Cut down the data a bit to reduce computation time
serial = serial[:10000]
	
covariance = np.zeros(len(serial))
state = np.zeros(len(serial))
state[0] = serial[0]

# Kalman filter
for i in range(1, len(serial)):
	xp = state[i - 1] + arduinoSecond
	pp = covariance[i] + arduinoUncertainty + gpsUncertainty
	innovation = serial[i] - xp
	innovationCovariance = pp + gpsUncertainty
	kalmanGain = pp / innovationCovariance
	state[i] = xp + kalmanGain * innovation
	covariance[i] = (1 - kalmanGain) * pp

offset = 10	
stateDT = np.zeros(len(state) - offset)
serialDT = np.zeros(len(serial) - offset)

for i in range(len(stateDT) - 1):
	stateDT[i] = state[i + 1 + offset] - state[i + offset]
	serialDT[i] = serial[i + 1 + offset] - serial[i + offset]
	print(stateDT[i], serialDT[i])
	
print("Kalman Standard Deviation:", np.std(stateDT))
print("Serial Standard Deviation:", np.std(np.asarray(serialDT)))
	
plt.scatter(range(len(stateDT)), stateDT, color = "red", label = "Kalman Filtered Deltas")
plt.scatter(range(len(serialDT)), serialDT, label = "Raw Deltas")
plt.legend()
plt.show()

histogramState, bins = np.histogram(stateDT, bins = range(0, 2000))
histogramSerial, bins = np.histogram(serialDT, bins = range(0, 2000))

plt.scatter(range(len(histogramState)), histogramState, color = "red", label = "Kalman Filtered Deltas")
plt.scatter(range(len(histogramSerial)), histogramSerial, label = "Raw Deltas")
plt.legend()
plt.show()