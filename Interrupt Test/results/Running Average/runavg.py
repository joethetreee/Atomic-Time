import numpy as np
import matplotlib.pyplot as plt

def running_mean(x, N):
	cumsum = np.cumsum(np.insert(x, 0.0, 0.0)) 
	return (cumsum[N:] - cumsum[:-N]) / N 

f = open("serial.txt", 'r')

data = f.read()
data = data.split("\n")

cuAvg = np.zeros(len(data))
sum = 0

offset = 0
stop = 200

for i, line in enumerate(data):
	if 900 < float(line) < 1100 and i > offset and i < stop:
		sum += float(line) - 1000
		cuAvg[i] = sum / (i + 1 - offset)
		print(cuAvg[i])
	
# Trim trailing zeros
cuAvg = list(cuAvg)
while not cuAvg[-1]:
	cuAvg.pop()
	
plt.scatter(range(len(cuAvg)), cuAvg)
plt.show()
	
	
dataShort = np.asarray(data[:10000], dtype = "float")
avgN = 10
cumSum = running_mean(dataShort, avgN)

plt.scatter(range(len(dataShort)), dataShort, color = "green", label = "Raw Data")
plt.scatter(range(len(cumSum)), cumSum, color = "red", label = "Moving Average N = {0}".format(avgN))
plt.legend()

plt.title("Serial Delta Time against Sample Number")
plt.ylabel("Delta Time (ms)")
plt.xlabel("Sample Number")

plt.show()
	
	
