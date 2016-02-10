
"""
removes failed data entries
"""

filename = "GARNMEA01"
linStart = ["$GPRMC","$GPGGA","t"] 		 	 	# start of each line

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

i = 0 									# iterates through contentsTxt
goodLines = [0]*len(contentsTxt) 					# stores indices of "good" lines
gli = 0									# keep track of index for good line

while(i<len(contentsTxt)):
	goodLine = True
	for j in range(len(linStart)):
		if (contentsTxt[i+j][:len(linStart[j])] != linStart[j]): 	# check that the line has the correct start
			i += j+1
			goodLine = False
			break
	print(i, goodLine)
	if (goodLine):
		for k in range(len(linStart)):
			goodLines[gli] = i
			i += 1
			gli += 1

print(gli)
goodLines = goodLines[:gli]
			
				

contents = open("../../Results/"+filename+"Chckd.txt", mode='w')		# open/create file to write

for i in range(len(goodLines)):
	contents.write(str(contentsTxt[goodLines[i]]))
	print(i,str(contentsTxt[goodLines[i]]))
	
contents.close()