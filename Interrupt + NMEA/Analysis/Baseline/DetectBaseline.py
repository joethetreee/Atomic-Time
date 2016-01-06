# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:54:25 2015

@author: Duncan
"""

import KalmanFilter as klm
import numpy as np
import matplotlib.pyplot as plt

filename = "GPSMIL33ChckdCor"
utm = 250 					# uncertainty in measured time
utp = 0.5 					# uncertainty in predicted time
avg_T = 1000 				# average time

countTarget = 10				# target number of ser_dTf on one side of avg_T before detecting new phase
count = 0 					# number of ser_dTf on one side of avg_T (+: above, -: below)

# extract data into arrays

contents = open(filename+".txt", mode='r')
contentsTxt = contents.readlines()
contents.close()

ser_Tm = [0]*len(contentsTxt)
pps_T = [0]*len(contentsTxt)

j = 0
for i in range(len(contentsTxt)):
	line = contentsTxt[i]
	if (line[0]=='t'):
		commaLoc = line.index(',')
		ser_Tm[j] = int(line[1:commaLoc])
		pps_T[j] = int(line[commaLoc+1:])
		j += 1
		
ser_Tm = ser_Tm[0:200]
pps_T = pps_T[0:200]

ser_dTm = [ser_Tm[1+i]-ser_Tm[i] for i in range(len(ser_Tm)-1)] 	# difference in time between measured serials
ser_Tf = [0]*len(ser_Tm) 			 	 	 	  	 	# Kalman filtered time, with resets
ser_Tf2 = [0]*len(ser_Tm) 			 	 	 	  	 	# Kalman filtered time 2nd order, with resets
ser_Tf_ = [0]*len(ser_Tm) 			 	 	 	  	 	# Kalman filtered time, without resets
ser_dTf = [0]*(len(ser_Tf)-1) 		 	 	 	 	 	# difference in time between filtered time
ser_Tb = [0]*(len(ser_Tm)) 							# stores times for baseline


ser_Uf = [0]*len(ser_Tf) 								# uncertainty in filtered time
ser_Uf_ = [0]*len(ser_Tf_) 							# uncertainty in filtered time
ser_Uf2 = [0]*len(ser_Tf2) 							# uncertainty in filtered time

avg_T = (pps_T[-1]-pps_T[0])
if (avg_T<0): avg_T += 60*60*24
avg_T /= (len(pps_T)-1)
print("avg_T: ", avg_T)

ser_Uf[0] = utm
ser_Uf_[0] = utm
ser_Tf[0] = ser_Tm[0]
ser_Tf_[0] = ser_Tm[0]
ser_Tf2[0] = ser_Tm[0]
serser_dTf = [0]*(len(ser_Tf)-1)
serser_dTf2 = [0]*(len(ser_Tf)-1)
ser_Tb[0] = ser_Tf[0]

cResetLast=0


# cycle through data and use Kalman filter.
# Reset Kalman when there is a jump in the baseline (detected from consistent skew in filtered dt values)
# baseline takes average value for the period -- need to register start and end for region
# problem: not all fall into one region -- there are sometimes drifts between regions

region_i = 0 										# start of region
region_f = 0 										# end of region
region_b = False 									# whether we are in a region
j=1
while(j<(len(ser_Tf))):
	# Kalman filter to find baseline (with resets)
	(ser_Tf[j], ser_Uf[j]) = klm.KalFilIter(ser_Tf[j-1],avg_T,ser_Tm[j], ser_Uf[j-1],utp,utm, 1,1,1)
	# Kalman filtered baseline
	(ser_Tf2[j], ser_Uf2[j]) = klm.KalFilIter(ser_Tf2[j-1],avg_T,ser_Tf[j], ser_Uf2[j-1],utp,ser_Uf[j], 1,1,1)
	# just Kalman filter
	(ser_Tf_[j], ser_Uf_[j]) = klm.KalFilIter(ser_Tf_[j-1],avg_T,ser_Tm[j], ser_Uf_[j-1],utp,utm, 1,1,1)
	serser_dTf[j-1] = ser_Tf[j]-ser_Tf[j-1]
	serser_dTf2[j-1] = ser_Tf2[j]-ser_Tf2[j-1]
	
	# increase count in direction of skew
	dCount = np.sign(serser_dTf2[j-1]-avg_T)
	if (np.sign(dCount)==-np.sign(count)): 	# reset count if skew has changed
		count = 0
		print("Turn off",j)
		if (region_b==False):
			region_b = True
			region_i = j
	else:
		count += dCount
	
	#print(count, serser_dTf[j-1],ser_Tf[j],ser_Tm[j],avg_T,j)
	
	print("count",count, cResetLast, j)
	# if count reaches target restart Kalman filter from here
	if (j==(len(ser_Tf)-1) or (abs(count)>=countTarget)): 	# cResetLast makes sure we don't get endless loop
		#print("back ",j,count)
		print("CountT",cResetLast,j)
		if (j!=(len(ser_Tf)-1)):
			cResetLast = j
			if (j==cResetLast):
				j -= (countTarget-1)
			else:
				j -= countTarget
		#ser_Tf[j] = int((ser_Tm[j]+ser_Tm[j-1]+avg_T)/2)
		jPrime = min(j+1,len(ser_Tf)-1)
		ser_Tf[j] = int((ser_Tm[j]+ser_Tm[jPrime]-(jPrime-j)*avg_T)/2)
		ser_Uf[j] = utm
		ser_Tf2[j] = ser_Tf[j]
		ser_Uf2[j] = utm
		count = 0
		region_b = False
		region_f = j 				# region has terminated
		
		if (region_f>region_i): 	# check whether region has a (positive) length
			reg_dtTot = (ser_Tf[region_f]-ser_Tf[region_i])
			reg_dt = reg_dtTot/(region_f-region_i) 	# average second length in region
			
			sqrtAvg = 0
			for k in range(region_i, region_f):
				sqrtAvg += np.power(ser_Tf[k+1]-ser_Tf[k],1/4) 
			sqrtAvg /= (region_f-region_i)
			sqrtAvg = np.power(sqrtAvg,4)
			sqrtAvg = 1000
			
			region_Tio = 0
			for k in range(region_f-region_i):
				region_Tio += ser_Tf[region_i+k]-(ser_Tf[region_i]+k*sqrtAvg)
			region_Tio /= (region_f-region_i)
			
			print("~",region_i, region_f, reg_dt)
			print("~",sqrtAvg, region_Tio)
			
			k = region_i	
			while (k<region_f): 	# we have finished a new baseline region -- fill it in
				ser_Tb[k] = ser_Tf[region_i]+region_Tio+(k-region_i)*reg_dt
				print(k,ser_Tf[k],ser_Tb[k])
				k += 1
		else:
			k = region_i	
			while (k<region_f): 	# we have finished a new baseline region -- fill it in
				ser_Tb[k] = ser_Tf[region_i]+region_Tio+(k-region_i)*reg_dt
				print(k,ser_Tf[k],ser_Tb[k])
				k += 1
		
	if (region_b==False): 			# not in baseline region; just add to baseline the normal filtered value
		ser_Tb[j] = ser_Tf[j]
		#print(".",j,ser_Tf[j],ser_Tb[j])
	
	j += 1
	
ppsser_dT = [ser_Tm[i]-pps_T[i] for i in range(len(pps_T))]
ppsser_dTf = [ser_Tf[i]-pps_T[i] for i in range(len(pps_T))]
ppsser_dTf_ = [ser_Tf_[i]-pps_T[i] for i in range(len(pps_T))]
ppsser_dTf2 = [ser_Tf2[i]-pps_T[i] for i in range(len(pps_T))]
ppsser_dTb = [ser_Tb[i]-pps_T[i] for i in range(len(pps_T))]
	
ser_ser ,= plt.plot(ppsser_dT)
#ser_fil ,= plt.plot(ppsser_dTf)
ser_fil_ ,= plt.plot(ppsser_dTf_)
ser_fil2 ,= plt.plot(ppsser_dTf2)
#ser_bas ,= plt.plot(ppsser_dTb)
plt.legend([ser_ser,ser_fil_,ser_fil2] , ["pps-ser","pps-KFil","pps-KFil baseline"])
plt.show()