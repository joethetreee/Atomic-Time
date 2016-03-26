# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 16:53:10 2015

@author: Duncan

"""
from numpy import sign

def KalFilIter(xf_, dxp, xm, uf_, dup, um, A=1, B=1, H=1):
	"""
	Performs one iteration of Kalman filter
	"""
	""" Input variables
	returns (xf,uf)
	x,u: filter variable and its uncertainty; -f,d--p,-m: filtered, difference, measured; _: previous
	A: mixing factor for last measurement contribution; B: mixing factor for dxp; H: convert between measurement, state
	"""
	""" Working variables
	-t: temporary
	d-: difference
	"""	
	xft = xf_ + A*dxp 				# temporary new prediction of state
	upt = A*uf_*A + dup 				# temporary new prediction of uncertainty
	dx = xm - xft 					# difference between measurement and temp prediction
	umt = H*upt*H + um 				# temporary new measurement uncertainty
	K = upt*H/umt 					# Kalman gain
	xf = xft + K*dx 					# new filtered time
	uf = (1-K*H)*upt 					# new filtered uncertainty
	
	return (xf,uf)
	
def KalFilMult(dxp,xm,dup,um,A=1,B=1,H=1,xfi="none",ufi="none"):
	""" Input variables
	returns (xf,uf)
	x,u: filter variable and its uncertainty; -f,-m,-i: filtered, measured, initial; _: previous
	A: mixing factor for last measurement contribution; B: mixing factor for dxp; H: convert between measurement, state
	"""
	""" Working variables
	-t: temporary
	d-: difference
	"""	
	# get the length of variables -- how long to apply the filter for
	length = max(len(dxp),len(xm))
	if (len(dxp)==0):
		dxp =[dxp]*length
	if (len(xm)==0):
		xm =[xm]*length
	if (len(dup)==0):
		dup =[dup]*length
	if (len(um)==0):
		um =[um]*length
		
	# specify initial filter values
	if (xfi == "none"):
		xfi = xm[0]
	if (ufi == "none"):
		ufi = um[0]
		
	# create filter array
	xf = [xfi]*length
	uf = [ufi]*length
	
	# apply filter
	for i in range(1,length,1):
		(xf[i],uf[i]) = KalFilIter(xf[i-1],dxp[i],xm[i],uf[i-1],dup[i],um[i],A,B,H)
	
	return(xf,uf)
	
	
def KalBaseline(xm,up,um,A=1,B=1,H=1, countT=10):
	""" Input variables
	returns (xf,uf)
	x,u: filter variable and its uncertainty; -f,-m: filtered, measured; _: previous
	A: mixing factor for last measurement contribution; B: mixing factor for dxp; H: convert between measurement, state
	countT: number of consecutive skewed values before the baseline is ended
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
	
	avg_x = (xm[-1]-xm[0])/(len(xm)-1)
	
	uf1[0] = um
	uf2[0] = um
	xf1[0] = xm[0]
	xf2[0] = xm[0]
	xb[0] = xf1[0]
	
	cResetLast=0
	ib = [] 							  	 	# stores list of indices[x,y] which form range
											# of flat baselines (from x->y inclusive)
	
	# cycle through data and use Kalman filter.
	# Reset Kalman when there is a jump in the baseline (detected from consistent skew in filtered values)
	# baseline takes average value for the period -- need to register start and end for region
	# problem: not all fall into one region -- there are sometimes drifts between regions
	
	jCur = 0
	
	def FindBaselineSection(xi,xf):
		"""
		xi: starting index
		xf: ending index (inclusive)
		Finds the baseline for a section; returns the index for the end of the baseline
		(last index in the baseline)
		If there is no baseline to begin with the current index is returned
		"""
		dirn = sign(xf-xi) 					# direction of change
		ip = xi 								# previous index
		ic = xi+dirn 							# current index
		count = 0
		while((ic<=xf)^(dirn==-1)): 			# find out if we have finished
			# Kalman filter to find baseline (with resets)
			(xf1[ic], uf1[ic]) = KalFilIter(xf1[ip],avg_x*dirn,xm[ic], uf1[ip],up,um, 1,1,1)
			# Kalman filtered baseline
			(xf2[ic], uf2[ic]) = KalFilIter(xf2[ip],avg_x*dirn,xf1[ic], uf2[ip],up,uf1[ic], 1,1,1)
			d_x2x2 = xf2[ic]-xf2[ip]
			
			# increase count in direction of skew
			dCount = sign(d_x2x2-avg_x)
			if (dCount==-sign(count)): 	# reset count if skew has changed
				count = 0
			else:
				count += dCount
			if (abs(count)>=countT):
				return ip-countT*dirn
			ip = ic
			ic += dirn
				
	while(True):
		print("jCur",jCur)
		jPrev = jCur
		xf1[jCur-1] = (xm[jCur]+xm[jCur-1]+avg_x)/2 	 	# set the previous filtered value to avg of last
		jCur = FindBaselineSection(jCur, length) 	 	# find index of end of current baseline
		if (jCur!=jPrev): 						 	# check whether there a baseline
			print("ib:",ib)
			ib.append([0,jCur]) 					 	# add the region to list
			print("ib:",ib)
			if (len(ib)<=1): 					 	 	# check whether there is a previous region
				ib[-1][0] = 0 					 	# use previous region to bound the current baseline
			jPrev = FindBaselineSection(jCur,ib[-1][0]) 	# work backwards to find start of region
			ib[-1][0] = jPrev
			
			for i_ in range(ib[-1][0],ib[-1][1]+1,1): 	# assign baseline values
				xb[i_] = xf2[i_]
				ub[i_] = uf2[i_]
			jCur += 1 							 	# add one if we have the end of a baseline
		jCur += 1
		if (jCur >= length):
			return (xb,ub,ib)