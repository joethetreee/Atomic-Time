# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 17:54:25 2015

@author: Duncan
"""

import KalmanFilter as klm
import numpy as np
import matplotlib.pyplot as plt

filename = "GPSMIL33ChckdCor"
utm = 100 					# uncertainty in measured time
utp = 0.5 					# uncertainty in predicted time
avg_T = 1000 				# average time

countTarget = 20				# target number of ser_dTf on one side of avg_T before detecting new phase
count = 0 					# number of ser_dTf on one side of avg_T (+: above, -: below)

def KalBaseline(xm,up,um,A=1,B=1,H=1, countTY=5, countTN=10):
	""" Input variables
	returns (xf,uf)
	x,u: filter variable and its uncertainty; -f,-m: filtered, measured; _: previous
	A: mixing factor for last measurement contribution; B: mixing factor for dxp; H: convert between measurement, state
	countTN: number of consecutive skewed values before the baseline is ended
	countTY: minimum size of baseline
	"""
	""" Working variables
	-t: temporary
	d-: difference
	"""	
	length = len(xm)
	xf1 = [0]*length 			 	 	 	 	# Kalman filtered value, with resets
	xf2 = [0]*length 			 	 	 	 	# Kalman filtered time 2nd order, with resets
	xb = [0]*length 						 	# stores times for baseline
	
	
	uf1 = [0]*length 						 	# uncertainty in filtered time
	uf2 = [0]*length 						 	# uncertainty in filtered time
	ub = [0]*length 							# uncertainty in baseline time
	
	avg_x = (xm[-1]-xm[0])/(len(xm)-1) 			# average difference
	avg_u = um/(len(xm)-1) 					# uncertainty in average value
#	avg_x = 1000.52
#	avg_u = 0
	print(avg_x)
	
	uf1[0] = um
	uf2[0] = um
	xf1[0] = xm[0]
	xf2[0] = xm[0]
	xb[0] = xf1[0]
	
	ib = [] 							  	 	# stores list of indices[x,y] which form range
											# of flat baselines (from x->y inclusive)
	
	# cycle through data and use Kalman filter.
	# Reset Kalman when there is a jump in the baseline (detected from consistent skew in filtered values)
	# baseline takes average value for the period -- need to register start and end for region
	# problem: not all fall into one region -- there are sometimes drifts between regions
	
	jCur = 1
	
	def FindBaselineSection(xi,xf,xAvg_,uAvg_):
		"""
		xi: starting index
		xf: ending index (inclusive)
		Finds the baseline for a section; returns the index for the end of the baseline
		(last index in the baseline)
		If there is no baseline to begin with the current index is returned
		"""
		dirn = klm.sign(xf-xi) 					# direction of change
		ip = xi-dirn 								# previous index
		ic = xi 							 	 	# current index
		count = 0
		while(klm.sign(ic-xf)!=dirn): 			  		# find out if we have finished
			# Kalman filter to find baseline (with resets)
			(xf1[ic], uf1[ic]) = klm.KalFilIter(xf1[ip],xAvg_*dirn,xm[ic], uf1[ip],uAvg_,um, 1,1,1)
			# Kalman filtered baseline
			#(xf2[ic], uf2[ic]) = klm.KalFilIter(xf2[ip],xAvg_*dirn,xf1[ic], uf2[ip],uAvg_,uf1[ic], 1,1,1)
			(xf2[ic], uf2[ic]) = (xf1[ic], uf1[ic])
			d_x2x2 = xf2[ic]-xf2[ip]
			
			# increase count in direction of skew
			dCount = klm.sign(d_x2x2-xAvg_*dirn)
			if (dCount==-klm.sign(count)): 	# reset count if skew has changed
				count = dCount
			else:
				count += dCount
			print("~",ic,ip,count,d_x2x2,xm[ic],xf1[ic],xf2[ic])
			if (abs(count)>=countTN):
				return ic-countTN*dirn
			ip = ic
			ic += dirn
		return ip
				
	while(True):
		print("jCur",jCur)
		jPrev = jCur
		xf1[jCur-1] = (xm[jCur]-avg_x+xm[jCur-1])/2 	 	# set the previous filtered value to avg of last
		xf2[jCur-1] = xf1[jCur-1]
		print("set",jCur-1,xf1[jCur-1])
		jCur = FindBaselineSection(jCur, length-1, avg_x, avg_u)# find index of end of current baseline
		print("FB",jCur,jPrev)
		if (jCur>jPrev+1): 						 	# check whether there a baseline
			continueOn = True
			ib.append([0,jCur]) 					 	# add the region to list
			if (len(ib)>1): 					 	 	# check whether there is a previous region
				ib[-1][0] = ib[-2][1]+1 				# use previous region to bound the current baseline
			avg_x_ = (xf2[ib[-1][1]]-xf2[ib[-1][0]])/(ib[-1][1]-ib[-1][0])
			d_xf2_ = [xf2[i+1]-xf2[i] for i in range(ib[-1][0],ib[-1][1])]
			avg_u_ = np.std(d_xf2_)
			(avg_x_,avg_u_) = klm.KalFilIter(avg_x,0,avg_x_,avg_u,avg_u,avg_u_,1,1,1)
			print("averages",avg_x,avg_u,";",avg_x_,avg_u_)
			jPrev = FindBaselineSection(jCur-1,ib[-1][0], avg_x_, avg_u) 	# work backwards to find start of region
			print("FB",jPrev)
			if (jCur-jPrev<countTY):
				ib = ib[:-1]
				continueOn = False
			if(continueOn):
				for i_ in range(ib[-1][0],ib[-1][1]+1,1): 	# assign baseline values
					xb[i_] = xf2[i_]
					ub[i_] = uf2[i_]
				avg_x_ = (xb[ib[-1][1]]-xb[ib[-1][0]])/(ib[-1][1]-ib[-1][0])
				d_xb_ = [xb[i+1]-xb[i] for i in range(ib[-1][0],ib[-1][1])]
				avg_u_ = np.std(d_xb_)
				(avg_x,avg_u) = klm.KalFilIter(avg_x,0,avg_x_,avg_u,avg_u,avg_u_,1,1,1)
				print("averages",avg_x,avg_u)
				print("ib:",ib[-1])
			#jCur += 1 							 	# add one if we have the end of a baseline
		jCur += 2
		if (jCur >= length):
			return (xb,ub,ib,xf1,xf2)

# extract data into arrays

contents = open("../../Results/"+filename+".txt", mode='r')
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
		
ser_Tm = ser_Tm[0:1000]
pps_T = pps_T[0:1000]

(serb_T,serb_U,serb_i,serf1_T,serf2_T) = KalBaseline(ser_Tm,0.5,150,1,1,1,5,10)

ppsserb_dT = []
ppsserb_i = []
ppsser_dT = [ser_Tm[i]-pps_T[i] for i in range(len(ser_Tm))]
ppsserf1_dT = [serf1_T[i]-pps_T[i] for i in range(len(serf1_T))]
ppsserf2_dT = [serf2_T[i]-pps_T[i] for i in range(len(serf2_T))]
sumx = 0
sumy = 0
k = 0
for i in range(len(serb_i)):
	sumx += serb_i[i][1]-serb_i[i][0]
	sumy += serb_T[serb_i[i][1]]-serb_T[serb_i[i][0]]
	
	for j in range(serb_i[i][0],serb_i[i][1]+1):
		ppsserb_dT.append(serb_T[k]-pps_T[j])
		ppsserb_i.append(j)
		k += 1

print("ib:",serb_i)
print("avg:",sumy/max(1,sumx),"true:",(pps_T[-1]-pps_T[0])/(len(pps_T)-1),";",(ser_Tm[-1]-ser_Tm[0])/(len(ser_Tm)-1),(serf1_T[-1]-serf1_T[0])/(len(serf1_T)-1))

for i in range(len(serb_i)):
	y = [serb_T[j]-serb_T[serb_i[i][0]] for j in range(serb_i[i][0],serb_i[i][1]+1,1)]
	x = range(serb_i[i][1]-serb_i[i][0]+1)
	
	print(np.correlate(x,y)/np.correlate(x,x))


#secLenArr = [(serb_T[serb_i[i][1]]-serb_T[serb_i[i][0]])/(serb_i[i][1]-serb_i[i][0]) for i in range(len(serb_i))]
#secLenWeightArr = [1/np.sqrt(serb_i[i][1]-serb_i[i][0]-1) for i in range(len(serb_i))]
#
#secLenAvg = 0
#for i in range(len(secLenArr)):
#	secLenAvg += secLenArr[i]*secLenWeightArr[i]
#secLenAvg /= sum(secLenWeightArr)
#
#secLenStd = 0
#for i in range(len(secLenArr)):
#	secLenStd += ((secLenArr[i]-secLenAvg)**2)*secLenWeightArr[i]
#secLenStd = np.sqrt(secLenStd)
#secLenStd /= np.sqrt(sum(secLenWeightArr))
#	
#print(secLenArr)
#
#print("secLenAvg:",secLenAvg)
#print("secLenStd:",secLenStd)
#
#secLenArrCut = []
#secLenWeightArrCut = []
#for i in range(len(secLenArr)):
#	if (abs(secLenArr[i]-secLenAvg)<secLenStd):
#		secLenArrCut.append(secLenArr[i])
#		secLenWeightArrCut.append(secLenWeightArr[i])
#
#print(secLenArrCut)
#
#secLenAvgCut = 0
#for i in range(len(secLenArrCut)):
#	secLenAvgCut += secLenArrCut[i]*secLenWeightArrCut[i]
#secLenAvgCut /= sum(secLenWeightArrCut)
#
#secLenStdCut = 0
#for i in range(len(secLenArrCut)):
#	secLenStdCut += ((secLenArrCut[i]-secLenAvgCut)**2)*secLenWeightArrCut[i]
#secLenStdCut = np.sqrt(secLenStdCut)
#secLenStdCut /= sum(secLenWeightArrCut)
#
#print("secLenAvgCut:",secLenAvgCut)
#print("secLenStdCut:",secLenStdCut)


#plt.plot(ppsserb_i,ppsserb_dT)
plt.scatter(range(len(ppsser_dT)),ppsser_dT, linewidth=0, s=2)
plt.xlim(0,len(ppsser_dT)-1)
plt.plot(ppsserf1_dT)
plt.plot(ppsserf2_dT)

#
#
#ser_dTm = [ser_Tm[1+i]-ser_Tm[i] for i in range(len(ser_Tm)-1)] 	# difference in time between measured serials
#ser_Tf = [0]*len(ser_Tm) 			 	 	 	  	 	# Kalman filtered time, with resets
#ser_Tf2 = [0]*len(ser_Tm) 			 	 	 	  	 	# Kalman filtered time 2nd order, with resets
#ser_Tf_ = [0]*len(ser_Tm) 			 	 	 	  	 	# Kalman filtered time, without resets
#ser_dTf = [0]*(len(ser_Tf)-1) 		 	 	 	 	 	# difference in time between filtered time
#ser_Tb = [0]*(len(ser_Tm)) 							# stores times for baseline
#
#
#ser_Uf = [0]*len(ser_Tf) 								# uncertainty in filtered time
#ser_Uf_ = [0]*len(ser_Tf_) 							# uncertainty in filtered time
#ser_Uf2 = [0]*len(ser_Tf2) 							# uncertainty in filtered time
#ser_Ub = [0]*len(ser_Tb) 							 	# uncertainty in baseline time
#
#avg_T = (pps_T[-1]-pps_T[0])
#if (avg_T<0): avg_T += 60*60*24
#avg_T /= (len(pps_T)-1)
#print("avg_T: ", avg_T)
#
#ser_Uf[0] = utm
#ser_Uf_[0] = utm
#ser_Uf2[0] = utm
#ser_Tf[0] = ser_Tm[0]
#ser_Tf_[0] = ser_Tm[0]
#ser_Tf2[0] = ser_Tm[0]
#serser_dTf = [0]*(len(ser_Tf)-1)
#serser_dTf2 = [0]*(len(ser_Tf)-1)
#ser_Tb[0] = ser_Tf[0]
#
#cResetLast=0
#ser_bVals = [] 									# stores list of [x,y] which form range of flat
#												# baselines (from x->y inclusive)
#
## cycle through data and use Kalman filter.
## Reset Kalman when there is a jump in the baseline (detected from consistent skew in filtered dt values)
## baseline takes average value for the period -- need to register start and end for region
## problem: not all fall into one region -- there are sometimes drifts between regions
#
#region_i = 0 										# start of region
#region_f = 0 										# end of region
#region_b = False 									# whether we are in a region
#j=1
#while(j<(len(ser_Tf))):
#	# Kalman filter to find baseline (with resets)
#	(ser_Tf[j], ser_Uf[j]) = klm.KalFilIter(ser_Tf[j-1],avg_T,ser_Tm[j], ser_Uf[j-1],utp,utm, 1,1,1)
#	# Kalman filtered baseline
#	(ser_Tf2[j], ser_Uf2[j]) = klm.KalFilIter(ser_Tf2[j-1],avg_T,ser_Tf[j], ser_Uf2[j-1],utp,ser_Uf[j], 1,1,1)
#	# just Kalman filter
#	(ser_Tf_[j], ser_Uf_[j]) = klm.KalFilIter(ser_Tf_[j-1],avg_T,ser_Tm[j], ser_Uf_[j-1],utp,utm, 1,1,1)
#	serser_dTf[j-1] = ser_Tf[j]-ser_Tf[j-1]
#	serser_dTf2[j-1] = ser_Tf2[j]-ser_Tf2[j-1]
#	
#	# increase count in direction of skew
#	dCount = np.sign(serser_dTf2[j-1]-avg_T)
#	if (np.sign(dCount)==-np.sign(count)): 	# reset count if skew has changed
#		count = 0
#		print("Turn off",j)
#		if (region_b==False):
#			region_b = True
#			region_i = j
#	else:
#		count += dCount
#	
#	#print(count, serser_dTf[j-1],ser_Tf[j],ser_Tm[j],avg_T,j)
#	
#	print("count",count, cResetLast, j)
#	# if count reaches target restart Kalman filter from here
#	if (j==(len(ser_Tf)-1) or (abs(count)>=countTarget)): 	# cResetLast makes sure we don't get endless loop
#		#print("back ",j,count)
#		print("CountT",cResetLast,j)
#		if (j!=(len(ser_Tf)-1)):
#			j_old = j 				 	 	# store the value
#			j -= countTarget 					# take off count target so it can work its way back up
#			if (len(ser_bVals)>0):
#				j = max(j, ser_bVals[-1][1]+1) 	# make sure we don't re-write a finished baseline
#			if (j_old==cResetLast): 			# check whether we have already tried to restart from here
#				j += 1 						# restart from one place further on
#			cResetLast = j 					# store latest place that we restarted
#		#ser_Tf[j] = int((ser_Tm[j]+ser_Tm[j-1]+avg_T)/2)
#		jPrime = min(j+1,len(ser_Tf)-1)
#		ser_Tf[j] = int((ser_Tm[j]+ser_Tm[jPrime]-(jPrime-j)*avg_T)/2)
#		ser_Uf[j] = utm
#		ser_Tf2[j] = ser_Tf[j]
#		ser_Uf2[j] = utm
#		count = 0
#		region_b = False
#		region_f = j 				# region has terminated
#		
#		if (region_f>region_i): 	# check whether region has a (positive) length
#			reg_dtTot = (ser_Tf[region_f]-ser_Tf[region_i])
#			reg_dt = reg_dtTot/(region_f-region_i) 	# average second length in region
#			
#			sqrtAvg = 0
#			for k in range(region_i, region_f):
#				sqrtAvg += np.power(ser_Tf[k+1]-ser_Tf[k],1/4) 
#			sqrtAvg /= (region_f-region_i)
#			sqrtAvg = np.power(sqrtAvg,4)
#			sqrtAvg = 1000
#			
#			region_Tio = 0
#			for k in range(region_f-region_i):
#				region_Tio += ser_Tf[region_i+k]-(ser_Tf[region_i]+k*sqrtAvg)
#			region_Tio /= (region_f-region_i)
#			
#			print("~",region_i, region_f, reg_dt)
#			print("~",sqrtAvg, region_Tio)
#			
#			ser_Tb[region_f] = ser_Tf2[region_f]
#			ser_Ub[region_f] = ser_Uf2[region_f]
#			k = region_f-1
#			while (k>=region_i): 	# we have finished a new baseline region -- fill it in
#				(ser_Tb[k], ser_Ub[k]) = klm.KalFilIter(
#					ser_Tb[k+1],-avg_T,ser_Tf[k], ser_Ub[k+1],utp,ser_Uf[k], 1,1,1)
#				print(k,ser_Tf[k],ser_Tb[k])
#				k -= 1
#			ser_bVals.append([region_i,region_f])
#		else:
#			k = region_i	
#			while (k<region_f): 	# we have finished a new baseline region -- fill it in
#				ser_Tb[k] = ser_Tf[region_i]+region_Tio+(k-region_i)*reg_dt
#				print(k,ser_Tf[k],ser_Tb[k])
#				k += 1
#		
#	if (region_b==False): 			# not in baseline region; just add to baseline the normal filtered value
#		ser_Tb[j] = ser_Tf[j]
#		#print(".",j,ser_Tf[j],ser_Tb[j])
#	
#	j += 1
#	
#ppsser_dT = [ser_Tm[i]-pps_T[i] for i in range(len(pps_T))]
#ppsser_dTf = [ser_Tf[i]-pps_T[i] for i in range(len(pps_T))]
#ppsser_dTf_ = [ser_Tf_[i]-pps_T[i] for i in range(len(pps_T))]
#ppsser_dTf2 = [ser_Tf2[i]-pps_T[i] for i in range(len(pps_T))]
#ppsser_dTb = [ser_Tb[i]-pps_T[i] for i in range(len(pps_T))]
#	
#ser_ser ,= plt.plot(ppsser_dT)
##ser_fil ,= plt.plot(ppsser_dTf)
##ser_fil_ ,= plt.plot(ppsser_dTf_)
#ser_fil2 ,= plt.plot(ppsser_dTf2)
#ser_bas ,= plt.plot(ppsser_dTb)
#plt.legend([ser_ser,ser_fil2,ser_bas] , ["pps-ser","pps-KFil baseline","baseline"])
#plt.show()