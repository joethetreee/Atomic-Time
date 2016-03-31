# -*- coding: utf-8 -*-
"""
Created on March 28th 2016

@author: jw32g12
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

		
# Load the NMEA file
f = open("../../results/GPSMIL37ChckdCor.txt")
data = f.read().split("\n")

i = 0
numSats = []

# Extract SV numbers and determine standard deviations of PPS Ser distributions.
while i < len(data) - 1:
	gga = data[i]
	rmc = data[i + 1]
	t = data[i + 2]
	t = t[1:]
	t = t.split(",")
	tser = int(t[0])
	tpps = int(t[1])
	sats = int(gga.split(",")[7])
	
	numSats.append(sats)
	
	i += 3
	


# Get starting conditions
i = 0
ppsser = []

# Apply Kalman filter to data from Interrupt + NMEA dataset.
while i < len(data) - 1:
	# Parse data from text file
	gga = data[i]
	rmc = data[i + 1]
	t = data[i + 2]
	t = t[1:]
	t = t.split(",")
	
	# Serial arrival time
	tser = int(t[0])
	
	# PPS arrival time
	tpps = int(t[1])
	
	ppsser.append(tser - tpps)
	
	# Go to next measurement
	i += 3

	
# Set the colour map
cmap = cm.gist_rainbow

# define the bins and normalize
bounds = np.linspace(min(numSats), max(numSats), max(numSats) - min(numSats) + 1)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
scalarMap = cm.ScalarMappable(norm = norm, cmap = cmap)

""" Plot the basic serial - PPS deltas """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))

# Axis titles
ax.set_title("GPS PPS - Serial Offset")
ax.set_xlabel("Sample")
ax.set_ylabel("GPS PPS - Serial Offset (ms)")
ax.set_xlim(0, len(ppsser))
ax.set_ylim(150, 400)
#ax.text(0.05, 0.9, "Standard Deviation = " + str(round(np.std(data), 2)) + "ms", transform = ax.transAxes)
ax.text(0.05, 0.88, "Using GPSMIL37ChckdCor.txt dataset", transform = ax.transAxes)

# Plot
ax.scatter(range(len(ppsser)), ppsser, linewidth = "0", s = 2)
plt.show()

""" Plot the basic kalman filtered PPS deltas """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

# Axis titles
ax.set_title("GPS PPS - Serial Offset as a Function of Connected Satellites")
ax.set_xlabel("Sample")
ax.set_ylabel("GPS PPS - Serial Offset (ms)")
ax.set_xlim(0, len(ppsser))
ax.set_ylim(150, 400)
#ax.text(0.05, 0.9, "Standard Deviation = " + str(round(np.std(data), 2)) + "ms", transform = ax.transAxes)
ax.text(0.05, 0.88, "Using GPSMIL37ChckdCor.txt dataset", transform = ax.transAxes)
ax2.set_ylabel("Number of Connected Satellites", size = 12)

# Plot
ax.scatter(range(len(ppsser)), ppsser, c = numSats, cmap = cmap, norm = norm, linewidth = "0", s = 2)
plt.show()