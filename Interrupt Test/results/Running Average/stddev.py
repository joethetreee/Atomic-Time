import numpy as np
import matplotlib.pyplot as plt

def running_mean(x, N):
	cumsum = np.cumsum(np.insert(x, 0.0, 0.0)) 
	return (cumsum[N:] - cumsum[:-N]) / N 

f = open("serial.txt", 'r')

data = f.read()
data = data.split("\n")
	
dataShort = np.asarray(data[:10000], dtype = "float")
cumSum = []
stdDev = []
avgN = 20

for N in np.arange(avgN):
	cumSum.append(running_mean(dataShort, N + 1))
	stdDev.append(np.std(cumSum[N]))
	
# Arduino Clock Errors
sums = np.zeros(avgN)
# Number of Arduino milliseconds per second
secondLength = 1.001
# for N in range(avgN):
	# for j in range(0, N):
		# sums[N] += secondLength * (j + 1)
	
	# if N:
		# sums[N] = sums[N] / N
sums = np.asarray([secondLength * N for N in range(avgN)])
	
plt.plot(range(len(stdDev)), stdDev, label = "StdDev of Running Avg")
plt.plot(range(len(stdDev)), np.ones(len(stdDev)), color = "red", label = "1ms Line")
plt.plot(range(len(sums)), sums, label = "Arduino Error")
plt.plot(range(len(sums)), sums + stdDev, color = "black", label = "Combined Error")
plt.legend()
plt.title("Running Average Standard Deviation against Number of Samples")
plt.ylabel("Standard Deviation (ms)")
plt.xlabel("Number of Samples N")
plt.show()
	
	
