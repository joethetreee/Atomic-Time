#ifndef H_TIMESTORE
#define H_TIMESTORE

#include "Arduino.h"
#include <DataAnalysis.h>

struct TimeEnc
{
	int h;
	int m;
	int s;
	int ms;
};

TimeEnc EncodeTime(unsigned long time_);
unsigned long DecodeTime(TimeEnc timeEnc_);

unsigned long AddTime(unsigned long t1, unsigned long t2, bool map=true);
TimeEnc AddTime(TimeEnc tEnc1, TimeEnc tEnc2, bool map=true);

unsigned long DecodeHHMMSS(unsigned long time_);
unsigned long DecodeHHMMSS(float time_);

class TimeStore
{
public:
	TimeStore(unsigned long time_);
	TimeStore(TimeEnc timeEnc_);
	TimeStore();
	~TimeStore();
	
	void SetTime(unsigned long time_);
	void SetTime(TimeEnc timeEnc_);
	
	void AddTime(unsigned long time_, bool map=true);
	void AddTime(TimeEnc timeEnc_, bool map=true);
	
	unsigned long GetTime();
	TimeEnc GetTimeEnc();
		
private:
	unsigned long time;
	TimeEnc timeEnc;
};

#endif