# kalman_pps_dt.py
# Author: Joe Wilson
# Takes a list of sequential PPS times and produces a txt file of
# delta times

import numpy as np
import matplotlib.pyplot as plt

file = "KL2PPS01"

f = open("results/{0}".format(file + ".txt"), "r")
dts = []

# Read in line seperated absolute milli times
dataIn = f.read().split("\n")

# Turn into time deltas between each update
for k in dataIn:
	dataTemp = k.split(",")
	dts.append(int(dataTemp[1]) - int(dataTemp[0]))
	
# Convert ints to strings and convert back into line seperated format
dts = [str(k) for k in dts]
data = "\n".join(dts)

# Produce histogram of successive time deltas
i = 1
histo = np.zeros(len(dataIn))
while i < len(dataIn):
	dataTemp = dataIn[i].split(",")
	time2 = int(dataTemp[0])
	dataTemp = dataIn[i - 1].split(",")
	time1 = int(dataTemp[0])
	
	histo[time2 - time1] += 1
	i += 1

# Write to file
# dt
outFile = open("results/{0}".format(file + "_dt.txt"), "w")
outFile.write(data)
outFile.close()
f.close()
# pps_dt
# Convert ints to strings and convert back into line seperated format
histoData = [str(k) + "," + str(v) for k,v in enumerate(histo)]
data = "\n".join(histoData)
outFile = open("results/{0}".format(file + "_ppsdt.csv"), "w")
outFile.write(data)
outFile.close()
f.close()

# Plot
plt.plot(range(len(dts)), dts)
plt.show()

# Delta histogram
fig, ax = plt.subplots(1, 1, figsize = (15, 10))
ax.plot(range(len(histo)), histo)
ax.set_title("Distribution of Successive Arduino Kalman PPS Time Deltas")
ax.set_xlabel("KALPPS - KALPPS Time Delta (ms)")
ax.set_ylabel("Frequency")
ax.set_xlim(975, 1025)
ax.grid()
ax.text(0.05, 0.88, "Using {0}.txt dataset".format(file), transform = ax.transAxes)
plt.show()