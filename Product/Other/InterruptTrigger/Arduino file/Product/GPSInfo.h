#ifndef H_GPSINFO
#define H_GPSINFO

#include "Arduino.h"
#include <DataAnalysis.h>
#include <TimeStore.h>

#define GGA_TIME 1
#define GGA_QUAL 6
#define GGA_SNUM 7

#define GGA_NUM 3
//#define GGA_ARR[GGA_NUM] {GGA_TIME, GGA_QUAL, GGA_SNUM}
#define RMC_TIME 1

extern unsigned int GGA_ARR[GGA_NUM];

class GPSInfo               // decodes NMEA sentences and extracts useful data
{
public:
  GPSInfo();
  ~GPSInfo();
  
  void DecodeGGA(String senGGA);
  void DecodeRMC(String senRMC);
  bool CheckConsistency();    // checks whether ~the times are consistent; ~the difference between current and last time rounds to 1000 ms
  bool CheckFix();

  unsigned long GetTime();
  unsigned long GetGGATime();
  unsigned long GetRMCTime();
  byte GetQual();
  byte GetSatNum();
private:
  unsigned long ggaTime;
  unsigned long rmcTime;
  unsigned long lastTime;       // time for previous data set (should be from 1 second before); given by the GGA time
  byte qual;
  byte sNum;
  bool consistent;
};

#endif
