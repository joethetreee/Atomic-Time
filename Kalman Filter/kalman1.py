# kalman1.py
# written by Greg Czerniak (email is greg {aT] czerniak [dOt} info )
#
# Implements a single-variable linear Kalman filter.
#
# Note: This code is part of a larger tutorial "Kalman Filters for Undergrads"
# located at http://greg.czerniak.info/node/5.
import random
import numpy
import matplotlib.pyplot as plt

# Implements a linear Kalman filter.
class KalmanFilterLinear:
  def __init__(self,_A, _B, _H, _x, _P, _Q, _R):
    self.A = _A                      # State transition matrix.
    self.B = _B                      # Control matrix.
    self.H = _H                      # Observation matrix.
    self.current_state_estimate = _x # Initial state estimate.
    self.current_prob_estimate = _P  # Initial covariance estimate.
    self.Q = _Q                      # Estimated error in process.
    self.R = _R                      # Estimated error in measurements.
  def GetCurrentState(self):
    return self.current_state_estimate
  def Step(self,control_vector,measurement_vector):
    #---------------------------Prediction step-----------------------------
    predicted_state_estimate = self.A * self.current_state_estimate + self.B * control_vector
    predicted_prob_estimate = (self.A * self.current_prob_estimate) * numpy.transpose(self.A) + self.Q
    #--------------------------Observation step-----------------------------
    innovation = measurement_vector - self.H*predicted_state_estimate
    innovation_covariance = self.H * predicted_prob_estimate * numpy.transpose(self.H) + self.R
    #-----------------------------Update step-------------------------------
    kalman_gain = predicted_prob_estimate * numpy.transpose(self.H) * numpy.linalg.inv(innovation_covariance)
    self.current_state_estimate = predicted_state_estimate + kalman_gain * innovation
    # We need the size of the matrix so we can make an identity matrix.
    size = self.current_prob_estimate.shape[0]
    # eye(n) = nxn identity matrix.
    self.current_prob_estimate = (numpy.eye(size)-kalman_gain*self.H)*predicted_prob_estimate

class Voltmeter:
  def __init__(self,_truevoltage,_noiselevel):
    self.truevoltage = _truevoltage
    self.noiselevel = _noiselevel
  def GetVoltage(self):
    return self.truevoltage
  def GetVoltageWithNoise(self):
    return random.gauss(self.GetVoltage(),self.noiselevel)

arduinoSecond = 1001.26
arduinoUncertainty = 1
gpsUncertainty = 500

A = numpy.matrix([1])
H = numpy.matrix([1])
B = numpy.matrix([1])
Q = numpy.matrix([arduinoUncertainty])
R = numpy.matrix([gpsUncertainty + arduinoUncertainty])
xhat = numpy.matrix([3])
P    = numpy.matrix([1])

filter = KalmanFilterLinear(A,B,H,xhat,P,Q,R)

file = open("PPSSER.csv", 'r')
serial = []
pps = []

# Extract data from file
for line in file:
	split = line.split(",")
	serial.append(int(split[0]))
	pps.append(int(split[1]))
	
# Cut down the data a bit to reduce computation time
serial = serial[:20000]

measuredvoltage = []
truevoltage = []
kalman = []

for i in range(1, len(serial)):
    measured = serial[i - 1]
    measuredvoltage.append(measured)
    truevoltage.append(1000 * i + pps[0])
    kalman.append(filter.GetCurrentState()[0,0])
    filter.Step(1000, numpy.matrix([measured]))
	
offset = 10	
stateDT = numpy.zeros(len(kalman) - offset)
serialDT = numpy.zeros(len(serial) - offset)

for i in range(len(stateDT) - 1):
	stateDT[i] = kalman[i + 1 + offset] - kalman[i + offset]
	serialDT[i] = serial[i + 1 + offset] - serial[i + offset]
	
print("Kalman Standard Deviation:", numpy.std(stateDT))
print("Serial Standard Deviation:", numpy.std(numpy.asarray(serialDT)))

plt.scatter(range(len(stateDT)), stateDT, color = "red", label = "Kalman Filtered Deltas")
plt.scatter(range(len(serialDT)), serialDT, label = "Raw Deltas")
plt.legend()
plt.xlabel("Sample Number N")
plt.ylabel("Delta Time (ms)")
plt.title("GPS Delta Time against Sample Number")
plt.show()