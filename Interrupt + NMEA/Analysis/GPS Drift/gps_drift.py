# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 2015

@author: Joe

Opens a formatted file and resaves as a CSV with NMEA data removed

"""

f = open("GPSMIL33.txt", 'r')
new = open("GPSMIL33_TIME.csv", 'a')

i = 0
for line in f:
	if line.startswith("t"):
		temp = line[1:].rstrip("\n")
		splt = temp.split(",")
		serTime = int(splt[0])
		ppsTime = int(splt[1])
		if not i:
			new.write(str(i) + "," + temp + "\n")
		else:
			new.write(str(i) + "," + temp + "," + str(serTime - serLast) + "," + str(ppsTime - ppsLast) + "," + str(serTime - ppsTime) + "\n")
		serLast = int(splt[0])
		ppsLast = int(splt[1])
		i += 1

f.close()
new.close()