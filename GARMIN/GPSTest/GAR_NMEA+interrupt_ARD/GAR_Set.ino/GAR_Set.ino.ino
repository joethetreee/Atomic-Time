#include <SoftwareSerial.h>
#include "String.h"
SoftwareSerial gps(8,9, true);
byte boadT = 4;
int boadCur = 9600;
uint32_t tLastSec = millis();
uint32_t tLastByte = millis();

//char* int2str(int val)
//{
//  byte power = 0;
//  while(pow(10,power)<val)
//    power++;
//  char* valStr = new char[power+1];
//
//  for (byte i=0; i<power; i++)
//  {
//    (valStr[power-1-i] = val%int(pow(10,i+1)))/pow(10,i);
//  }
//  valStr[power]='\0';
//  return valStr;
//}

void SetRMC(byte baudVal, byte pulseLenVal)
{
  String sendSentence_ = "PGRMC,,,,,,,,,,"+String(baudVal)+",,,"+String(2)+",";
  int chksumDec = 0;
  for (int i=0; ;i++)
  {
    if (sendSentence_[i]=='\0')
      break;
    chksumDec ^= sendSentence_[i];
  }  
  Serial.print("chksumDec: ");
  Serial.println(chksumDec);
  gps.print("$");
  Serial.print("$");
  gps.print(sendSentence_);
  Serial.print(sendSentence_);
  gps.print("*");
  Serial.print("*");
  gps.print(char(chksumDec/16+'0'));
  Serial.print(char(chksumDec/16+'0'));
  byte chksumHexCon = 0;
  if (chksumDec%16>9)
    chksumHexCon+=7;
  gps.print(char(chksumDec%16+'0'+chksumHexCon));
  Serial.print(char(chksumDec%16+'0'+chksumHexCon));
  gps.print(char(0xD));
  Serial.print(char(0xD));
  gps.print(char(0xA));
  Serial.print(char(0xA));
}

void SetRMO(char* GPType, byte val)
{
  String sendSentence_ = String("PGRMCO,")+String(GPType)+String(",")+String(val);
  int chksumDec = 0;
  for (int i=0; ;i++)
  {
    if (sendSentence_[i]=='\0')
      break;
    chksumDec ^= sendSentence_[i];
  }  
  Serial.print("chksumDec: ");
  Serial.println(chksumDec);
  gps.print("$");
  Serial.print("$");
  gps.print(sendSentence_);
  Serial.print(sendSentence_);
  gps.print("*");
  Serial.print("*");
  gps.print(char(chksumDec/16+'0'));
  Serial.print(char(chksumDec/16+'0'));
  byte chksumHexCon = 0;
  if (chksumDec%16>9)
    chksumHexCon+=7;
  gps.print(char(chksumDec%16+'0'+chksumHexCon));
  Serial.print(char(chksumDec%16+'0'+chksumHexCon));
  gps.print(char(0xD));
  Serial.print(char(0xD));
  gps.print(char(0xA));
  Serial.print(char(0xA));
}

void setup()
{
  pinMode(2, INPUT);
  pinMode(3, OUTPUT);
  gps.begin(boadCur);
  Serial.begin(9600);

  delay(2000);
  
  SetRMC(boadT,2);
  SetRMO("GPGSV",0); 
}

void loop()
{  

  if (gps.available())
  {
    uint32_t tCurByte = millis();
    if (tCurByte-tLastByte>100)         // if greater then we have new set of sentences => new second
    {
      uint32_t tCurSec = millis();
      Serial.println(tCurSec-tLastSec);
      tLastSec = tCurSec;
    }
    tLastByte = tCurByte;
    char txt = gps.read();
    Serial.print(txt);
  }
}
