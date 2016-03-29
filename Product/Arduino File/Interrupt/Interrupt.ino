#include <MinimumSerial.h>
#include <SdFat.h>
#include <SdFatConfig.h>
#include <SdFatmainpage.h>
#include <SdFatUtil.h>
#include <SdInfo.h>
#include <SdSpi.h>
#include <SdSpiCard.h>
#include <SPI.h>

#include <Timer.h>
#include <Button.h>

volatile uint32_t ppsMilli = 0;
volatile uint32_t ppsMilliLast = 0;
volatile uint32_t ppsMilli_ = 0;

volatile uint32_t serMilli = 0;
volatile uint32_t serMilliLast = 0;
volatile uint32_t serMilli_ = 0;

// SD Card
SdFat sd;
SdFile logfile;
bool sdActive = false;

byte pinButRes = 19;
byte pinButMod = 20;
byte pinLedFix = 22;
byte pinSDCS = 14;
byte pinGPSSerIn = 9;
byte pinGPSPps = 17;

bool serTrig = false;
bool ppsTrig = false;
bool fix = false;

Button bMod(pinButMod);
Button bRes(pinButRes);



// Software reset definitions
// __ __ __ __ __ __ __

#define RESTART_ADDR       0xE000ED0C
#define READ_RESTART()     (*(volatile uint32_t *)RESTART_ADDR)
#define WRITE_RESTART(val) ((*(volatile uint32_t *)RESTART_ADDR) = (val))

// blink out an error code
void error(uint8_t errno)
{ 
  // note: blink code won't work after sd.begin() because SPI disables pin13 LED!!! We must end SPI first
  TimerTarget ledErrDelay(millisecond, 200);
  byte i=0;
  byte k=0;
  SPI.end();
  
  while(!bMod.GetState()) {
    // if i<errno we flash errno times]
    if (i<errno)
    {
      // turn LED on/off when we end the last flash
      if (!ledErrDelay.GetRunning())
      {
        if (i==0)
          if (bRes.GetState()==1)
            WRITE_RESTART(0x5FA0004);
            
        digitalWrite(pinLedFix, (k+1)%2);
        ledErrDelay.Start(100);
      }
      // increment k (turn on->off or vice versa) and increment i
      if (ledErrDelay.Check())
      {
        k = (k+1)%2;
        ledErrDelay.Reset();
        i += int(k==0);
      }
    }
    // if i>=errno we end flashing and start waiting
    else if (i<10)
    {
      if (!ledErrDelay.GetRunning())
        ledErrDelay.Start(200);
      if (ledErrDelay.Check())
      {
        ledErrDelay.Reset();
        i++;
      }
    }
    // if i has been incremented errno times we reset 
    else
    {
      Serial.print("error ");
      Serial.println(errno);
      i=0;
    }
    bMod.UpdateState();
    bRes.UpdateState();
  }
}

void setup()
{
  pinMode(pinLedFix, OUTPUT);
  *portConfigRegister(pinButMod) = PORT_PCR_MUX(1) | PORT_PCR_PE;     // set as input with pulldown resistor
  *portConfigRegister(pinButRes) = PORT_PCR_MUX(1) | PORT_PCR_PE;     // set as input with pulldown resistor
  pinMode(pinGPSSerIn, INPUT);
  pinMode(pinGPSPps, INPUT);
  
  if (Serial1)
  {
    Serial.begin(9600);
    Serial.println("begin");
  }

  // Chip select
  pinMode(pinSDCS, OUTPUT);
  digitalWriteFast(pinSDCS, HIGH);
  InitialiseSDFile();

  attachInterrupt(digitalPinToInterrupt(pinGPSSerIn), GetSerTime, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinGPSPps), GetPPSTime, RISING);
}
void InitialiseSDFile()
{
  sdActive = true;
  if (!sd.begin(pinSDCS, SPI_HALF_SPEED))
  {
    sdActive = false;
    error(2);
  }
  char filename[15];
  strcpy(filename, "INTPRD00.TXT");
  for (uint8_t i = 0; i < 100; i++)
  {
    filename[6] = '0' + i/10;
    filename[7] = '0' + i%10;
    // create if does not exist, do not open existing, write, sync after write
    if (! sd.exists(filename))
    {
      break;
    }
  }
  if (sdActive)
    if (!logfile.open(filename, O_RDWR | O_CREAT | O_AT_END))
    {
      sdActive = false;
      error(3);
    }
}

void loop()
{
  if (millis()>ppsMilliLast+1000 && fix)
  {
    Serial.println("nofix");
    fix = false;
    digitalWrite(pinLedFix, 0);
  }
  if (ppsTrig && serTrig)
  {
    Serial.print(serMilliLast);
    Serial.print(",");
    Serial.println(ppsMilliLast);
    if (sdActive)
    {
      logfile.print(serMilliLast);
      logfile.print(",");
      logfile.println(ppsMilliLast);
      logfile.flush();
    }
    fix = true;
    digitalWrite(pinLedFix, 1);
  }
}

void GetSerTime()
{
  serMilli = millis();
  if (serMilli > serMilliLast+250 && serMilli > serMilli_+200 && ppsTrig)
  {
    serMilliLast = serMilli;
    serTrig = true;
  }
  serMilli_ = serMilli;
}

void GetPPSTime() {
  ppsMilli = millis();
  if (ppsMilli > ppsMilliLast+250)
  {
    ppsMilliLast = ppsMilli;
    ppsTrig = true;
  }
}
