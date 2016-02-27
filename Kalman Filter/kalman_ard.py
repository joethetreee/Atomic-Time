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
		avgs[j] = np.average(np.nonzero(distroResults[j]))
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
	gga = data[i]
	rmc = data[i + 1]
	t = data[i + 2]
	t = t[1:]
	t = t.split(",")
	tser = int(t[0])
	tpps = int(t[1])
	sats = int(gga.split(",")[7])
	
	filterPPS.step(1000, tser - avgs[sats] + avgs[startSats])
	filter.step(1000, tser)
	kalResults.append(filter.currentStateEstimate - tpps)
	kalResultsPPS.append(filterPPS.currentStateEstimate - tpps)
	
	i += 3
	
print("kalResults PPS Compensation stdDev", np.std(kalResultsPPS))
print("kalResults stdDev", np.std(kalResults))
  
# Set the colour map
cmap = cm.gist_rainbow

# define the bins and normalize
bounds = np.linspace(min(numSats), max(numSats), max(numSats) - min(numSats) + 1)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

""" Plot the basic kalman filtered PPS deltas """
fig, ax = plt.subplots(1, 1, figsize = (15, 10))

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

# Axis titles
ax.set_title("Kalman Filtered Predicted PPS as a Function of Connected Satellites")
ax.set_xlabel("Sample")
ax.set_ylabel("GPS PPS - Kalman PPS Offset")
ax.set_xlim(0, len(kalResults))
ax.set_ylim(150, 350)
ax.text(1000, 340, "Standard Deviation = " + str(np.std(kalResults)))
ax.text(1000, 335, "Using GPSMIL37ChckdCor.txt dataset")
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
ax.set_title("Kalman Filtered Predicted PPS with Satellite Time Offset")
ax.set_xlabel("Sample")
ax.set_ylabel("GPS PPS - Kalman PPS Offset")
ax.set_xlim(0, len(kalResultsPPS))
ax.set_ylim(150, 350)
ax.text(1000, 340, "Standard Deviation = " + str(np.std(kalResultsPPS)))
ax.text(1000, 335, "Using GPSMIL37ChckdCor.txt dataset")
ax2.set_ylabel("Number of Connected Satellites", size = 12)

# Plot
ax.scatter(range(len(kalResultsPPS)), kalResultsPPS, c = numSats, cmap = cmap, norm = norm, linewidth = "0", s = 2)
plt.show()

""" Plot the PPS - Ser distributions """
fig, ax = plt.subplots(1, 1)

# create a second axes for the colorbar
ax2 = fig.add_axes([0.91, 0.1, 0.03, 0.8])
cb = mpl.colorbar.ColorbarBase(ax2, cmap = cmap, norm = norm, spacing = 'proportional', ticks = bounds, boundaries = bounds, format = '%1i')

# Plot
for i in range(len(distroResults)):
	ax.scatter(range(len(distroResults[i])), distroResults[i], c = [i] * len(distroResults[i]), cmap = cmap, norm = norm, linewidth = "0", s = 2)
	
plt.show()