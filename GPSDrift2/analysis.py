import pynmea2
import time
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime
import math

if __name__ == "__main__":

	fileList = [None] * 100

	i = 1
	for file in os.listdir("results"):
		if file.endswith(".TXT") or file.endswith(".txt"):
			print(i, "-", file)
			fileList[i] = file
			i += 1
			
			
	num = int(input("Enter file number\n"))
	print("")

	data = open("results/" + fileList[num], 'r')
	
	x = 0
	y = []
	numRecords = 0
	freq = np.zeros(3000, int)
	
	for line in data:
		if line.startswith("$GPGGA"):
		
			tempList = line.split(",")
			timeMillis = int(tempList[-1].rstrip("\n"))
			tempList = tempList[:-1]
			nmea = ",".join(tempList)
			
			try:
				nmeaMsg = pynmea2.parse(nmea)
				freq[timeMillis] += 1
				y.append(timeMillis)
				numRecords += 1
				#print(x)
				
			except pynmea2.nmea.ChecksumError as err:
				print("Checksum")
			except pynmea2.nmea.ParseError as err:
				print("Parse")
				
		x += 1

	data.close()
	
	avgMillis = sum(y) / len(y)
	print(avgMillis)
	
	plt.plot(range(len(freq)), freq)
	plt.title("Delta Time Frequency for {0} Samples".format(math.ceil(numRecords)))
	plt.xlim(750, 1250)
	plt.xlabel("Delta Time (ms)")
	plt.ylabel("Frequency")
	plt.show()
	
	print("")
	os.system("pause")