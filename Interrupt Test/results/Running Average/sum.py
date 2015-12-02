import numpy as np
import matplotlib.pyplot as plt


avgN = 200
# Arduino Clock Errors
sums = np.zeros(avgN)
# Number of Arduino milliseconds per second
secondLength = 1
for N in range(avgN):
	for j in range(0, N):
		sums[N] += secondLength * (j + 1)
	
	if N:
		sums[N] = sums[N] / N
	
plt.plot(range(len(sums)), sums)
plt.show()
	
