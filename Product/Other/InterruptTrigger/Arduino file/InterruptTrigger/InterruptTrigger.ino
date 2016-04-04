#include <TimeStore.h>
#include <DataAnalysis.h>
#include <SoftwareSerial.h>


volatile long serSendTime0 = 0;     // time of sending (time inside interrupt)
volatile long ppsSendTime0 = 0;
volatile long serSendTime1 = 0;     // time of finishing interrupt (after sending)
volatile long ppsSendTime1 = 0;

volatile long serStartTarget = 0;
volatile long ppsStartTarget = 0;
volatile long serStopTarget = 0;
volatile long ppsStopTarget = 0;

//int serMsgLen = 100;
int ppsMsgLen = 100;

volatile byte serState = 2;         // 0: waiting to start emit __ 1: emitting __ 2: finished emitting, will send info
volatile byte ppsState = 2;

byte pinSerOut = 2;
byte pinPpsOut = 3;
byte pinPrint = 4;

// random variables
// our random signal is composed of
/// base (varies on long time scale) and
/// noise (rapidly varying

int avgbaseoffset = 270;              // guide for offset
int avgbasewidth = 80;                // guide for width
int avgbaselenMin = 60;           // number of seconds over which the base varies
int avgbaselenMax = 2000;         // number of seconds over which the base varies

int baseoffset = 0;               // 
int baselen = 0;

int avgnoisewidthBig = 0;         // adjacent main lobes
int avgnoisewidthSmall = 10;      // adjacent small lobes
int avgnoisewidthFine = 1;        // fine

bool firstRun = true;

String msgGGA = "$GPGGA,000000,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47\0";
String msgRMC = "$GPRMC,000000,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A\0";
unsigned long msgTime = 0;

SoftwareSerial ser(5,pinSerOut);

int Sign(int input)
{
  return (int(input>0)-int(input<0));
}

int GetRandomBaseoffset() // distributed such that the probability is higher to go closer to the avgbaseoffset
{
  int offsetSize = baseoffset + random(avgbasewidth/2/1.2, avgbasewidth*1.2);
  int dirn = Sign(random(avgbaseoffset-baseoffset-avgbasewidth, avgbaseoffset-baseoffset+avgbasewidth));

  int newbaseoffset = baseoffset + dirn*offsetSize;

  // check whether we are too far out and correct
  if (abs(newbaseoffset-avgbaseoffset)>avgbasewidth*1.5)
  {
    newbaseoffset -= Sign(baseoffset-avgbaseoffset)*random(avgbasewidth*0.1, avgbasewidth*0.3);
  }
  return newbaseoffset;
}

int GetRandomBaselen()
{
  return random(avgbaselenMin, avgbaselenMax);
}

int GetRandomNoiseoffset()
{
  int newnoiseoffset = 0;

  int bigoffset = 0;
  bigoffset = random(-3,3);
  if (abs(bigoffset)==3)
    bigoffset/=3;
  else bigoffset = 0;
  bigoffset*=avgnoisewidthBig;
  
  int smalloffset = 0;
  int fineoffset = 0;
  byte target = 20;
  for (byte i=0; i<target; i++)
  {
    smalloffset += random(-1,1)*avgnoisewidthSmall;
    fineoffset += random(-1,1)*avgnoisewidthFine;
  }

  newnoiseoffset = avgbaseoffset+bigoffset+smalloffset+fineoffset;
  return newnoiseoffset;
}

void setup()
{
  pinMode(pinSerOut, OUTPUT);
  pinMode(pinPpsOut, OUTPUT);
  pinMode(pinPrint, INPUT);
  
  if (Serial)
  {
    Serial.begin(9600);
  }

  ser.begin(9600);
  randomSeed(analogRead(0));
}

void loop()
{
  CheckPpsTime();
  CheckSerTime();
}

void CheckPpsTime()
{
  unsigned long t = millis();
  if (t>=ppsStartTarget && ppsState==0)
  {
    digitalWrite(pinPpsOut, 1);
    ppsState ++;
  }
  else if (t>=ppsStopTarget && ppsState==1)
  {
    digitalWrite(pinPpsOut, 0);
    ppsState ++;
  }
}

void CheckSerTime()
{
  unsigned long t = millis();
  if (t>=serStartTarget&& serState==0)
  {
    ser.println(msgGGA);
    ser.println(msgRMC);
    serState =2;
  }
  else if (serState>1 && ppsState>1)
  {
    if (digitalRead(pinPrint && !firstRun))
    {
      Serial.print(serStartTarget);
      Serial.print(",");
      Serial.println(ppsStartTarget);
//      Serial.println(msgGGA);
//      Serial.println(msgRMC);
    }
    else
    {
//      Serial.print("noHigh ");
//      Serial.print(serStartTarget);
//      Serial.print(",");
//      Serial.println(ppsStartTarget);
//      Serial.println(msgGGA);
//      Serial.println(msgRMC);
    }

    // increase time in message
    msgTime = AddTime(msgTime,1000,true);
    TimeEnc msgEnc = EncodeTime(msgTime);
    String strTime = "000000";
    strTime[0]=char('0'+msgEnc.h/10);
    strTime[1]=char('0'+msgEnc.h%10);
    strTime[2]=char('0'+msgEnc.m/10);
    strTime[3]=char('0'+msgEnc.m%10);
    strTime[4]=char('0'+msgEnc.s/10);
    strTime[5]=char('0'+msgEnc.s%10);
//    Serial.println(strTime);
//    Serial.println(msgTime);
//    Serial.print(msgEnc.s);
//    Serial.print(" ");
//    Serial.println(msgEnc.ms);

    for (byte i=0; i<6; i++)
    {
      msgGGA[7+i] = strTime[i];
      msgRMC[7+i] = strTime[i];
    }

    ppsStartTarget += 1000;
    ppsStopTarget = ppsStartTarget + ppsMsgLen;

    if (baselen<=0)
    {
      baselen = GetRandomBaselen();
      baseoffset = GetRandomBaseoffset();
    }

    serStartTarget = ppsStartTarget + baseoffset + GetRandomNoiseoffset();
    serStopTarget = serStartTarget + ppsMsgLen;
      
    serState = 0;
    ppsState = 0;
    
    baselen --;
    firstRun = false;
  }
}

