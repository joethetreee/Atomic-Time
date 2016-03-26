#include "GPSInfo.h"

unsigned int GGA_ARR[GGA_NUM] = {GGA_TIME, GGA_QUAL, GGA_SNUM};

GPSInfo::GPSInfo()
{
  ggaTime = 0;
  rmcTime = -1;
}
GPSInfo::~GPSInfo()
{}

void GPSInfo::DecodeGGA(String senGGA)
{
  lastTime = ggaTime;
  int* values = ExtractValuesInt(senGGA, ',', GGA_ARR, GGA_NUM);
  consistent = (values[0]==GGA_NUM);       // check whether the number of good values

  if (consistent)
  {
    ggaTime = DecodeHHMMSS((unsigned long)values[1]);
    qual = values[2];
    sNum = values[3];
  }
  CheckConsistency();

  delete [] values;
}
void GPSInfo::DecodeRMC(String senRMC)
{
  rmcTime = DecodeHHMMSS((unsigned long)ExtractValueInt(senRMC, ',', RMC_TIME));
  CheckConsistency();
}
bool GPSInfo::CheckConsistency()
{
  consistent = true;
  if (int((ggaTime-rmcTime+0.5)/1000)!=0)
    consistent = false;
  if (int((ggaTime-lastTime+0.5)/1000)!=1)
    consistent = false;

  return consistent;
}
bool GPSInfo::CheckFix()
{
  return consistent&&(qual!=0);
}

unsigned long GPSInfo::GetTime()
{
  return ggaTime;
}
unsigned long GPSInfo::GetGGATime()
{
  return ggaTime;
}
unsigned long GPSInfo::GetRMCTime()
{
  return rmcTime;
}
byte GPSInfo::GetQual()
{
  return qual;
}
byte GPSInfo::GetSatNum()
{
  return sNum;
}
