# -*- coding: utf-8 -*-
"""
Created on March 31st 2016

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
ppspps = np.zeros(2000)

ppsOld = 0

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
	
	try:
		ppspps[tpps - ppsOld] += 1
	except IndexError:
		# Lost lock
		pass
	
	ppsOld = tpps
	
	i += 3
	
fig, ax = plt.subplots(1, 1, figsize = (15, 10))
ax.bar(range(len(ppspps)), ppspps, align = 'center')
ax.set_title("Distribution of GPS PPS - PPS Time Deltas")
ax.set_xlabel("Time Delta (ms)")
ax.set_ylabel("Frequency")
ax.set_xlim(995, 1005)
ax.set_xticks(range(995, 1005)) 
plt.show()