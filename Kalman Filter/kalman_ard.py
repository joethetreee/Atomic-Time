# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 12:16:15 2016

Test bed for Kalman filter based Arduino clocks

@author: jw32g12
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Kalman filter class
class KalmanFilter:
	
	A = 1
	B = 1
	H = 1
	Q = 1

	currentStateEstimate = 0
	currentProbEstimate = 0
	innovation = 0
	kalmanGain = 0
	predictedStateEstimate = 0
	predictedPropEstimate = 0
	
	def __init__(self, arduinoUncertainty, gpsUncertainty, currentStateEstimate):
		self.R = gpsUncertainty
		self.Q = arduinoUncertainty
		self.currentStateEstimate = currentStateEstimate
		
	def step(self, controlVector, measurementVector):
		self.predictedStateEstimate = self.A * self.currentStateEstimate + self.B * controlVector;
		self.predictedProbEstimate = self.A * self.currentProbEstimate * self.A + self.Q;
			
		# Observation
		self.innovation = measurementVector - self.H * self.predictedStateEstimate;
		self.innovationCovariance = self.H * self.predictedProbEstimate * self.H + self.R;
		
		# Update
		self.kalmanGain = self.predictedProbEstimate * self.H / self.innovationCovariance;
		self.currentStateEstimate = self.predictedStateEstimate + self.kalmanGain * self.innovation;
		self.currentProbEstimate = (1 - self.kalmanGain * self.H) * self.predictedProbEstimate;
		
# Load the NMEA file
f = open("GPSMIL37ChckdCor.txt")
data = f.read().split("\n")

arduinoUncertainty = 0.5
gpsUncertainty = 500

i = 0
kalResults = []
kalResultsPPS = []
kalFilterPPS = []
kalFilter = []
distroResults = np.zeros( (12, 1000) )
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
	
	distroResults[sats][tser - tpps] += 1
	numSats.append(sats)
	
	i += 3
	
# Get averages of distributions
avgs = np.zeros(max(numSats) + 1)

for j in range(max(numSats) + 1):
	if np.any(distroResults[j]):
		# Average of distribution
		avgs[j] = np.sum(range(len(distroResults[j])) * distroResults[j]) / np.sum(distroResults[j])
		
		# Peak of distribution
		#avgs[j] = np.argmax(distroResults[j])
		
		print(avgs[j])
	else:
		avgs[j] = 0

	
# Get starting conditions
i = 0
gga = data[i]
rmc = data[i + 1]
t = data[i + 2]
t = t[1:]
t = t.split(",")
tser = int(t[0])
tpps = int(t[1])
sats = int(gga.split(",")[7])
startSats = sats

filter = KalmanFilter(arduinoUncertainty, gpsUncertainty, tser)
filterPPS = KalmanFilter(arduinoUncertainty, gpsUncertainty, tser)

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
	
	# Number of satellites from the GGA message
	sats = int(gga.split(",")[7])
	
	# Do kalman filter step whilst compensating for satellite number delay
	filterPPS.step(1000, tser - avgs[sats] + avgs[startSats])
	
	# Do a standard kalman filter
	filter.step(1000, tser)
	
	# Add results to an array
	kalResults.append(filter.currentStateEstimate - tpps)
	kalResultsPPS.append(filterPPS.currentStateEstimate - tpps)
	kalFilterPPS.append(filterPPS.currentStateEstimate)
	kalFilter.append(filter.currentStateEstimate)
	
	# Go to next measurement
	i += 3
	
print("kalResults PPS Compensation stdDev", np.std(kalResultsPPS))
print("kalResults stdDev", np.std(kalResults))

# Calculate kalman pps - kalman pps time deltas
ppsDeltas = np.zeros(1100)
deltas = np.zeros(1100)
for k in range(1, len(kalResultsPPS)):
	ppsDeltas[kalFilterPPS[k] - kalFilterPPS[k - 1]] += 1
	deltas[kalFilter[k] - kalFilter[k - 1]] += 1
	
  
# Set the colour map
cmap = cm.gist_rainbow

# define the bins and normalize
bounds = np.linspace(min(numSats), max(numSats), max(numSats) - min(numSats) + 1)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
scalarMap = cm.ScalarMappable(norm = norm, cmap = cmap)

""" Plot the basic kalman filtered PPS deltas """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

# Axis titles
ax.set_title("Kalman Filtered Predicted PPS as a Function of Connected Satellites")
ax.set_xlabel("Sample")
ax.set_ylabel("GPS PPS - Kalman PPS Offset (ms)")
ax.set_xlim(0, len(kalResults))
ax.set_ylim(150, 350)
ax.text(0.05, 0.9, "Standard Deviation = " + str(round(np.std(kalResults), 2)) + "ms", transform = ax.transAxes)
ax.text(0.05, 0.88, "Using GPSMIL37ChckdCor.txt dataset", transform = ax.transAxes)
ax2.set_ylabel("Number of Connected Satellites", size = 12)

# Plot
ax.scatter(range(len(kalResults)), kalResults, c = numSats, cmap = cmap, norm = norm, linewidth = "0", s = 2)
plt.show()

""" Plot the PPS distribution modified kalman data """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

# Axis titles
ax.set_title("Kalman Filtered Predicted PPS with Satellite Time Offset Average")
ax.set_xlabel("Sample")
ax.set_ylabel("GPS PPS - Kalman PPS Offset (ms)")
ax.set_xlim(0, len(kalResultsPPS))
ax.set_ylim(150, 350)
ax.text(0.05, 0.9, "Standard Deviation = " + str(round(np.std(kalResultsPPS), 2)) + "ms", transform = ax.transAxes)
ax.text(0.05, 0.88, "Using GPSMIL37ChckdCor.txt dataset", transform = ax.transAxes)
ax2.set_ylabel("Number of Connected Satellites", size = 12)

# Plot
ax.scatter(range(len(kalResultsPPS)), kalResultsPPS, c = numSats, cmap = cmap, norm = norm, linewidth = "0", s = 2)
plt.show()

""" Plot the PPS - Ser distributions """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))
ax.set_xlim(200, 400)
ax.set_title("Serial - PPS Time Offset Distribution")
ax.set_xlabel("Time Offset (ms)")
ax.set_ylabel("Frequency")
ax.text(0.05, 0.88, "Using GPSMIL37ChckdCor.txt dataset", transform = ax.transAxes)

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

# Plot
for i in range(len(distroResults)):
	c = cmap((i - min(numSats)) * (max(numSats) + 1) / ((max(numSats) - min(numSats) + 1) * 10))
	ax.plot(range(len(distroResults[i])), distroResults[i], color = c)
	ax.axvline(avgs[i], c = c)
	ax.text(avgs[i], 400 - i * 8, str(i), color = c)
	
plt.show()

""" Plot the kalman PPS - kalmanPPS time deltas distribution """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))
ax.set_xlim(np.nonzero(ppsDeltas)[0][0] - 5, np.nonzero(ppsDeltas)[0][-1] + 15)
ax.set_title("Kalman PPS - Kalman PPS Time Delta Distribution Average")
ax.set_xlabel("Time Delta (ms)")
ax.set_ylabel("Frequency")
ax.text(0.05, 0.88, "Using GPSMIL37ChckdCor.txt dataset", transform = ax.transAxes)

ax.plot(range(len(deltas)), deltas, color = "red", label = "Base Kalman")
ax.plot(range(len(ppsDeltas)), ppsDeltas, color = "blue", label = "SV Compensated Kalman")
ax.legend(loc = 0)
ax.grid()

plt.show()