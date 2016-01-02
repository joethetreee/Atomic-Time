# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 16:02:24 2016

@author: Duncan
"""


filename = "ardTim20160101_145412"

file = open(filename+".txt", "r")
contentsTxt = file.readlines()
file = file.close()

fileNew = open(filename+"_.txt", "w")

for line in contentsTxt:
	if (line!="\n" and len(line)>1):
		fileNew.write(line)
		
fileNew.close()