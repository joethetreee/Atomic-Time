
"""
removes failed data entries
"""

filename = "INTPRD01"
linStart = [""] 		 	 	# start of each line

contents = open("../../Results/"+filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

i = 0 									# iterates through contentsTxt
goodLines = [0]*len(contentsTxt) 					# stores indices of "good" lines
gli = 0									# keep track of index for good line
oset_per = 2								# number of entries per line

while(i<len(contentsTxt)):
	goodLine = True
	line = contentsTxt[i]
	if (line.count(',')!=oset_per-1):
		goodLine = False
	if (goodLine):
		for k in range(len(linStart)):
			goodLines[gli] = i
			i += 1
			gli += 1
	else:
		i += 1
		print("badline",i,line)

print(gli)
goodLines = goodLines[:gli]
			
				

contents = open("../../Results/"+filename+"Chk.txt", mode='w')		# open/create file to write

for i in range(len(goodLines)):
	line = str(contentsTxt[goodLines[i]])
	if (i==len(goodLines)-1):
		line = line[:-1]
	contents.write(line)
	
contents.close()