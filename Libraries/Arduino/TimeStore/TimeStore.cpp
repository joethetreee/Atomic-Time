#include "TimeStore.h"

TimeEnc EncodeTime(unsigned long time_)
{
	TimeEnc timeEnc_;
	
	unsigned long multF = 1000*60*60;
	timeEnc_.h = time_/multF;
	time_ -= timeEnc_.h*multF;
		
	multF/=60;
	timeEnc_.m = time_/multF;
	time_ -= timeEnc_.m*multF;
	
	multF/=60;
	timeEnc_.s = time_/multF;
	time_ -= timeEnc_.s*multF;
	timeEnc_.ms = time_;	
	
	return timeEnc_;
}

unsigned long DecodeTime(TimeEnc timeEnc_)
{
	unsigned long time_ = 0;
	unsigned long multF = 1000;
	time_ += timeEnc_.ms;
	time_ += timeEnc_.s*multF;
	multF*=60;
	time_ += timeEnc_.m*multF;
	multF*=60;
	time_ += timeEnc_.h*multF;
	
	return time_;
}


unsigned long DecodeHHMMSS(unsigned long time_)
{
	unsigned long time = 0;
	unsigned long multF=1000*60*60;
	
	time += (time_/10000)*multF;
	time_ = time_%10000;
	multF/=60;
	
	time += (time_/100)*multF;
	time_ = time_%100;
	multF/=60;
	
	time += time_*multF;
	return time;
}
unsigned long DecodeHHMMSS(float time_)
{
	unsigned long time = DecodeHHMMSS((unsigned long)time_);
	time += 1000*(time_ - (unsigned long)time_);
	return time;
}

unsigned long AddTime(unsigned long t1, unsigned long t2, bool map)
{
	unsigned long t = t1+t2;
	if (map)
		t%=(1000*60*60*24);
	return t;
}

TimeEnc AddTime(TimeEnc tEnc1, TimeEnc tEnc2, bool map)
{
	TimeEnc t;
	t.ms = tEnc1.ms+tEnc2.ms;
	t.s = tEnc1.s+tEnc2.s + t.ms/1000;
	t.ms = t.ms%1000;
	t.m = tEnc1.m+tEnc2.m + t.s/60;
	t.s = t.s%60;
	t.h = tEnc1.h+tEnc2.h + t.m/60;
	t.m = t.m%60;
	
	if (map)
		t.h %= 24;
	return t;
}

// TimeStore class
	TimeStore::TimeStore(unsigned long time_)
	{
		time = time_;
		timeEnc = EncodeTime(time);
	}
	TimeStore::TimeStore(TimeEnc timeEnc_)
	{
		timeEnc = timeEnc_;
		time = DecodeTime(timeEnc);
	}
	TimeStore::TimeStore()
	{
		time = 0;
		timeEnc = EncodeTime(time);
	}
	TimeStore::~TimeStore()
	{}
	
	void TimeStore::SetTime(unsigned long time_)
	{
		time = time_;
		timeEnc = EncodeTime(time);
	}
	void TimeStore::SetTime(TimeEnc timeEnc_)
	{
		timeEnc = timeEnc_;
		time = DecodeTime(timeEnc);
	}
	
	void TimeStore::AddTime(unsigned long time_, bool map)
	{
		time = ::AddTime(time, time_, map);
		timeEnc = EncodeTime(time);
	}
	void TimeStore::AddTime(TimeEnc timeEnc_, bool map)
	{
		timeEnc = ::AddTime(timeEnc, timeEnc_, map);
		time = DecodeTime(timeEnc);
	}
	
	unsigned long TimeStore::GetTime()
	{
		return time;
	}
	TimeEnc TimeStore::GetTimeEnc()
	{
		return timeEnc;
	}