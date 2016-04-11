# kalman_pps_dt.py
# Author: Joe Wilson
# Takes a list of sequential kalman PPS times and produces a graph of
# delta times

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl

file = "KL1PRD12ChkCor"

f = open("../../results/{0}".format(file + ".txt"), "r")
dts = []

# Read in line seperated absolute milli times
dataIn = f.read().split("\n")

# Make histogram of kalman pps - kalman pps time deltas
histo = np.zeros(2000)
for i in range(1, len(dataIn)):
	dataTemp1 = int(float(dataIn[i - 1].split(",")[2]))
	dataTemp2 = int(float(dataIn[i].split(",")[2]))
	
	histo[dataTemp2 - dataTemp1] += 1

# Make list of delta times	
dts = np.zeros(len(dataIn))
for i in range(1, len(dataIn)):
	dataTemp1 = int(float(dataIn[i - 1].split(",")[2]))
	dataTemp2 = int(float(dataIn[i].split(",")[2]))
	
	dts[i - 1] = dataTemp2 - dataTemp1
	
# Histogram of Kal PPS - PPS offset
ppshisto = np.zeros(200)
for i in range(len(dataIn)):
	dataTemp1 = int(float(dataIn[i].split(",")[1]))
	dataTemp2 = int(float(dataIn[i].split(",")[2]))
	
	ppshisto[dataTemp2 - dataTemp1 + 100] += 1
	
	
# Kal PPS - PPS delta times
ppsdts = np.zeros(len(dataIn))
numSats = []
for i in range(len(dataIn)):
	dataTemp1 = int(float(dataIn[i].split(",")[1]))
	dataTemp2 = int(float(dataIn[i].split(",")[2]))
	
	ppsdts[i] = dataTemp2 - dataTemp1
	numSats.append(int(dataIn[i].split(",")[3]))

# KalPPS - KalPPS Delta histogram
fig, ax = plt.subplots(1, 1, figsize = (15, 10))
ax.scatter(range(len(histo)), histo, marker = "x", color = "black")
ax.set_title("Distribution of Successive Teensy Kalman PPS Time Deltas")
ax.set_xlabel("KALPPS - KALPPS Time Delta (ms)")
ax.set_ylabel("Frequency")
ax.set_xlim(975, 1025)
ax.set_ylim(0, max(histo) * 1.1)
ax.grid()
ax.text(0.05, 0.88, "Using {0}.txt dataset".format(file), transform = ax.transAxes)
ax.text(0.05, 0.90, "Standard Deviation = {0}ms".format(round(np.std(dts), 2)), transform = ax.transAxes)

# KalPPS - PPS Delta histogram
fig, ax = plt.subplots(1, 1, figsize = (15, 10))
ax.scatter(range(-100, 100), ppshisto, marker = "x", color = "black")
ax.set_title("Distribution of Kalman PPS - PPS Time Deltas")
ax.set_xlabel("KALPPS - PPS Time Delta (ms)")
ax.set_ylabel("Frequency")
ax.set_ylim(min(ppshisto) * 1.1, max(ppshisto) * 1.1)
ax.grid()
ax.text(0.05, 0.88, "Using {0}.txt dataset".format(file), transform = ax.transAxes)
ax.text(0.05, 0.90, "Standard Deviation = {0}ms".format(round(np.std(ppsdts), 2)), transform = ax.transAxes)

# KalPPS - PPS Deltas

# Set the colour map
cmap = cm.gist_rainbow

# define the bins and normalize
bounds = np.linspace(min(numSats), max(numSats), max(numSats) - min(numSats) + 1)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
scalarMap = cm.ScalarMappable(norm = norm, cmap = cmap)

fig, ax = plt.subplots(1, 1, figsize = (15, 10))

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

ax.scatter(range(len(ppsdts)), ppsdts, marker = "x", c = numSats, cmap = cmap, norm = norm, s = 2)
ax.set_title("Successive Kalman PPS - PPS Time Deltas")
ax.set_xlabel("Sample")
ax.set_ylabel("KALPPS - PPS Time Delta (ms)")
ax.text(0.05, 0.88, "Using {0}.txt dataset".format(file), transform = ax.transAxes)
ax.text(0.05, 0.90, "Standard Deviation = {0}ms".format(round(np.std(ppsdts), 2)), transform = ax.transAxes)
ax.text(0.05, 0.92, "Average = {0}ms".format(round(np.average(ppsdts), 2)), transform = ax.transAxes)
ax2.set_ylabel("Number of Connected Satellites", size = 12)


plt.show()