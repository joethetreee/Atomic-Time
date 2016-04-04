"""
Created: 08/12/2015
Author: Joe Wilson
Description: Plots serial delta times with an overlay of GPS data for analysis.
"""

import pynmea2
import matplotlib.pyplot as plt
import numpy as np
import os
import math

if __name__ == "__main__":

	# Provide a list of files for selection
	fileList = [None] * 100

	i = 1
	for file in os.listdir("../../results"):
		if file.endswith(".TXT") or file.endswith(".txt"):
			print(i, "-", file)
			fileList[i] = file
			i += 1
			
			
	num = int(input("Enter file number\n"))
	print("")

	file = open("../../results/" + fileList[num], 'r')
	numLines = len(file.read().split("\n"))
	file.close()
	
	ggaList = [None] * int(numLines / 3)
	rmcList = [None] * int(numLines / 3)
	ppsList = np.zeros(int(numLines / 3))
	serList = np.zeros(int(numLines / 3))
	numSats = np.zeros(int(numLines / 3))
	fix = np.zeros(int(numLines / 3))
	
	file = open("../../results/" + fileList[num], 'r')
	
	# Extract data from file. Format is $GPGGA...\n$GPRMC...\nt<SERIAL MILLIS><PPS MILLIS>\n
	print("Extracting data...")
	for i, line in enumerate(file):
		j = math.floor(i / 3)
		if line.startswith("$GPGGA"):
			ggaList[j] = pynmea2.parse(line)
			numSats[j] = ggaList[j].num_sats
			fix[j] = ggaList[j].gps_qual
		elif line.startswith("$GPRMC"):
			rmcList[j] = pynmea2.parse(line)
		elif line.startswith("t"):
			lineTemp = line[1:]
			lineTemp = lineTemp.split(",")
			serList[j] = float(lineTemp[0])
			ppsList[j] = float(lineTemp[1])
		
	print("Data extracted.")
	print("Processing data...")
	
	#ggaList = ggaList[:1000]
	#serList = serList[:1000]
	#ppsList = ppsList[:1000]
	
	#ggaList = list(filter(None, ggaList))
	
	serDtList = np.zeros(len(serList), float)
	#fix = [j.gps_qual for j in ggaList]	
	hdop = []
	for j in ggaList:
		try:
			hdop.append(float(j.horizontal_dil))
		except Exception:
			hdop.append(-1)
	#print(hdop)
	
	for i in range(1, len(serList) - 1):
		serDtList[i] = serList[i] - serList[i - 1]
		
	gridDiff = [serList[i] - ppsList[i] for i in range(len(serList))]
		
	print("Data processed.")
	print("Plotting...")
	
	fig = plt.figure()
	
	ax = fig.add_subplot(111)
	ax.scatter(range(len(gridDiff)), gridDiff, label = "Ser - PPS")
	
	ax2 = ax.twinx()
	ax2.plot(range(len(numSats)), numSats, color = "red", label = "#SVs")
	
	#ax3 = ax.twinx()
	#ax3.plot(range(len(fix)), fix, color = "green", label = "Fix")
	
	#ax4 = ax.twinx()
	#ax4.plot(range(len(hdop)), hdop, color = "black", label = "HDoP")

	ax.set_ylim(200, 350)
	ax2.set_ylim(2, 11)
	#ax3.set_ylim(-1, 2)
	
	# Plot nothing on the original axis to get legend labels for all lines.
	ax.plot(0, 0, color = "red", label = "#SVs")
	#ax.plot(0, 0, color = "green", label = "Fix")
	#ax.plot(0, 0, color = "black", label = "HDoP")
	
	ax.legend()
	plt.show()