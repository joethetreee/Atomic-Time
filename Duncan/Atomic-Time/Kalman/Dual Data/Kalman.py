# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:19:25 2015

@author: Duncan

Use a Kalman filter on GPS serial data to predict the PPS arrial time

Kalman filter smooths time of GPS serial data arrival, use PPS-SER distribution average to get expected PPS time

We must supply uncertainties in GPS serial time (given by PPS_SER dist) and arduino time (~1 ms)
Also we use the *drift* on the arduino -- the average second length discrepency

Version 1: Kalman filter applied twice
"""
import numpy as np
import matplotlib.pyplot as plt
filename = "Set-3-DULETH13Cor"

# extract data into arrays

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_T = [0]*len(contentsTxt)
pps_T = [0]*len(contentsTxt)

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (',' in line):
		commaLoc = line.index(',')
		ser_T[j] = int(line[:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_T = ser_T[:j+1]
pps_T = pps_T[:j+1]
		
ser_T = ser_T[:50]
pps_T = pps_T[:50]


serE_T = [0]*len(ser_T)	 	# expected time of serial arrival
covU_T = [0]*len(ser_T)	 	# expected uncertainty
ardU_t = 0.5				# uncertainty in arduino times
ardD_t = 1.126			 	# arduino drift per millisecond (from post-analysis) - defined as ard_ms in 1s - 1000
serU_t = 150			 	# uncertainty in gps serial arrival times

def KalFil0_n(serE0_t_, ard_dt, ser_t, covU0_t_):
	''' serE_t_ is old expected serial arrival time, art_dt is diff in arduino time at serial arrival,
	ser_t is the time of serial arrival, covU_t_ is old covariance uncertainty. '''
	serE0_t = serE0_t_ + ard_dt 	# expected new serial time
	covU0_t = covU0_t_ + ardU_t 	# expected new covariance uncertainty
	serD_t = ser_t - serE0_t 	# difference between actual and expected serial time
	S = covU0_t + serU_t 		# innovation covariance
	K = covU0_t/S 			# Kalman gain
	serE0_t = serE0_t + K*serD_t 	# new estimate of serial time
	covU0_t = (1-K)*covU0_t 		# new estimate of covariance uncertainty
	
	return serE0_t, covU0_t

def KalFil1_n(serE1_t_, ard_dt, serE0_t_, covU1_t_, covU0_t):
	''' serE_t_ is old expected serial arrival time, art_dt is diff in arduino time at serial arrival,
	ser_t is the time of serial arrival, covU_t_ is old covariance uncertainty. '''
	serE1_t = serE1_t_ + ard_dt 	# expected new serial time
	covU1_t = covU1_t_ + ardU_t 	# expected new covariance uncertainty
	serD_t = serE0_t_ - serE1_t 	# difference between actual and expected serial time
	S = covU1_t + covU0_t 		# innovation covariance
	K = covU1_t/S 			# Kalman gain
	serE1_t = serE1_t + K*serD_t 	# new estimate of serial time
	covU1_t = (1-K)*covU1_t 		# new estimate of covariance uncertainty
	
	return serE1_t, covU1_t
	
covU_T[0] = 100
serE_T[0] = ser_T[0]

for i in range(len(serE_T)-1):
	serE_T[1+i], covU_T[1+i] = KalFil0_n(serE_T[i], 1000+ardD_t, ser_T[1+i], covU_T[i])
	
ppsserE_dT = [0]*len(serE_T)
for i in range(len(serE_T)):
	ppsserE_dT[i] = serE_T[i]-pps_T[i]
	
ppsser_dT = [0]*len(ser_T)
for i in range(len(ppsser_dT)):
	ppsser_dT[i] = ser_T[i]-pps_T[i]
	
	
serser_dT = [0]*(len(ser_T)-1)
for i in range(len(serser_dT)):
	serser_dT[i] = ser_T[1+i]-ser_T[i]
	
	
serEserE_dT = [0]*(len(serE_T)-1)
for i in range(len(serEserE_dT)):
	serEserE_dT[i] = serE_T[1+i]-ser_T[i]
	

	
plt.plot(serser_dT)
plt.plot(serEserE_dT)
plt.xlabel("samples ~ 1s interval")
plt.ylabel("time / ms")
plt.title("Expected Serial PPS difference using Kalman filter")