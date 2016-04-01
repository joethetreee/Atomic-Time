#include <MinimumSerial.h>
#include <SdFat.h>
#include <SdFatConfig.h>
#include <SdFatmainpage.h>
#include <SdFatUtil.h>
#include <SdInfo.h>
#include <SdSpi.h>
#include <SdSpiCard.h>
#include <SPI.h>

// include the library code:
#include "Definitions.h"

#include <LiquidCrystal.h>
#include <LiquidCrystalFast.h>
#include <SoftwareSerial.h>
#include <LCDFController.h>

#include <Timer.h>Missed second!
#include <Button.h>

#include <DataAnalysis.h>
#include <TimeStore.h>

#include "GPSInfo.h"

SoftwareSerial gpsSerial(pinGPSSerIn, pinGPSSerOut);

#define SENLEN 85
#define SENGGA 0
#define SENRMC 1
byte senNum = 2;
char* senPrefixTerm = "$GPRMC";    // this sentence is the last one in the list
char* senPrefixGGA = "$GPGGA";
char* senPrefixRMC = "$GPRMC";
char* senPrefixArr[2] = {senPrefixGGA, senPrefixRMC};
char senStore[3][SENLEN];
// format for serial store: {GPGGA, GPRMC, incoming data}

unsigned char dataPos;
bool willSend = false;
byte senLast = 0; // most recent sentence type to be identified
bool senTerm = false;                   // whether the sentence received is the last of the lot
unsigned long charTime = 0;             // time when the most recent character was read through serial (so if the data transfer fails we aren't left in serial mode with no interrupts)
int serialTimeout = 5;                  // time in ms since last character was read before timing out

bool initialFilter = true;                        // whether the next filter will be the very first one performed
bool firstNonLoop = false;
bool firstLoop = true;
bool firstMessageSet = true;                       // don't send the first one -- usually wrong
bool reading = false;


elapsedMicros myMicros = micros();             // clock time which updates automatically + handles rollover
//elapsedMicros myMicros = 4285000000;             // clock time which updates automatically + handles rollover
volatile double ppsMilli = 0;
volatile double ppsMilliLast = 0;
volatile double ppsMilli_ = 0;

volatile double serMilli = 0;
volatile double serMilliLast = 0;
volatile double serMilli_ = 0;

// initialize the library with the numbers of the interface pins
LCDFController lcd(pinLCDRS, pinLCDRW, pinLCDEn, pinLCDD4, pinLCDD5, pinLCDD6, pinLCDD7, 16, 2, lcdTimeUnit, lcdTimeRefresh);
//LiquidCrystalFast lcd(2,8,3, 4,5,6,7);

ButtonM bRes(pinButRes, 2);
Button bMod(pinButMod);

bool ppsEmit = false;                                   // whether PPS is being output

unsigned long timeGPSStream_act;                        // real-world time given by GPS serial stream
unsigned long timeGPSStream_ard;                        // arduino time at start of GPS serial stream
// Kalman variables
// filter outputs are arrays of multiple variables; the first is the current second prediction, the next are successive predictions from second length alone
// this is needed to deal with situations in which the filter predicts a time in the past (we estimate a second ahead to fix this)
#define PRED_NUM 3                                      // number of predictions to make
unsigned long sec_xf[PRED_NUM];                         // Kalman prediction of next second in Arduino time (in milliseconds)
float secRem_xf = 0;                                    // carries the remainder of prediction (<1ms)
float sec_uf[PRED_NUM];                                 // uncertainty in Kalman prediction
int sec_um = 50;                                        // uncertainty of timing from GPS receiver
float sec_dxp = 999.985;                                // prediction of second length
float sec_up = 1;                                   // uncertainty in prediction

GPSInfo gpsInfo;                                        // class used for interpreting GPS NMEA data
TimerTarget pulseTimer(millisecond, pulseLen);          // timer for outputting pulses


bool serialActive = false;

// SD Card
SdFat sd;
SdFile logfile;
bool sdActive = false;


byte pinTest = 15;

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
            
        digitalWriteFast(pinLedFix, (k+1)%2);
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
      if (serialActive)
      {
        Serial.print("error ");
        Serial.println(errno);
      }
      i=0;
    }
    bMod.UpdateState();
    bRes.UpdateState();
  }
}
//void Blink(byte pin, int t)
//{
//  TimerTarget ledErrBlink(millisecond, t);
//  for (byte k=0; k<2; k++)
//  {
//    ledErrBlink.Start();
//    digitalWriteFast(pin, k);
//    while(!ledErrBlink.Check());
//    ledErrBlink.reset();
//  }
//}

void setup()
{
  pinMode(pinLedPps, OUTPUT);
  pinMode(pinLedFix, OUTPUT);
  *portConfigRegister(pinButRes) = PORT_PCR_MUX(1) | PORT_PCR_PE;     // set as input with pulldown resistor
  *portConfigRegister(pinButMod) = PORT_PCR_MUX(1) | PORT_PCR_PE;     // set as input with pulldown resistor
  pinMode(pinGPSSerIn, INPUT);
  pinMode(pinGPSSerOut, OUTPUT);  
  pinMode(pinGPSPps, INPUT);
  pinMode(pinSDCS, OUTPUT);
  pinMode(pinPpsOut, OUTPUT);
  pinMode(pinTest, OUTPUT);

  digitalWriteFast(pinLedFix, LOW);
  
  if (Serial1)
  {
    Serial.begin(9600);
    serialActive = true;
    Serial.println("begin");
  }

  // Chip select
  pinMode(pinSDCS, OUTPUT);
  digitalWriteFast(pinSDCS, HIGH);
  InitialiseSDFile();

  gpsSerial.begin(9600);
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
  strcpy(filename, "KL1PRD00.TXT");
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
  RecordSerial();
  UpdateInput();
  UpdateOutput();
  CheckSecondTurn();
}

void RecordSerial()
{
  if (reading && millis()>charTime+serialTimeout)            // check for error in reading
  {
    gpsSerial.flush();
    if (serialActive)
      Serial.println("SerialTimeout");
    if (sdActive)
    {
      logfile.println("SerialTimeout");
      logfile.flush();
    }
    senTerm = true;
    reading = false;
    firstNonLoop = true;
  }
  if (gpsSerial.available())
  {
    charTime = millis();                          // register time of reading
    reading = true;
    //    if (dataPos == 0)
    //    {
    //      serMilliLast = millis();
    //    }
    // If this is the first time we've entered the loop, remove the interrupts so our serial reading isn't interrupted.
    if (firstLoop)
    {
      //detachInterrupt(digitalPinToInterrupt(pinGPSSerIn));
      //detachInterrupt(digitalPinToInterrupt(pinGPSPps));
      firstNonLoop = true;
      firstLoop = false;
    }
    volatile uint32_t serTCur = millis();
    char dataByte = char(gpsSerial.read());
    if (dataByte == 0xD || dataPos > SENLEN-3)    // check for end of sentence
    {
      while (dataByte != 0xA)
        dataByte = gpsSerial.read();
      if (willSend)
      {
        senStore[senNum][dataPos] = '\n';
        senStore[senNum][dataPos + 1] = '\0';
        willSend = false;

        // move sentence from temporary storage into its own array
        for (int i=0; i<SENLEN; i++)
          senStore[senLast][i] = senStore[senNum][i];

        Serial.print(senStore[senNum]);
      }
      dataPos = 0;
      reading = false;
    }
    if (reading)
    {
      if (dataPos < pow(2, sizeof(dataPos) * 8) - 3)
      {
        senStore[senNum][dataPos] = dataByte;
        dataPos++;
        Serial.print(dataByte);
      }
      if (dataPos == 7)
      {
        for (byte senType = 0; senType < senNum; senType++)
        {
          willSend = true;
          for (byte i = 0; i < 6; i++)
            willSend = willSend & (senPrefixArr[senType][i] == senStore[senNum][i]);
          if (willSend)
          {
            senLast = senType;
            break;
          }
        }
        // check whether we have the terminal sentence
        senTerm = true;
        for (byte i = 0; i < 6; i++)
          senTerm = senTerm & (senPrefixTerm[i] == senStore[senNum][i]);
      }
    }
  }
  // else: serial not available
  {
    if (firstNonLoop && !reading && senTerm)                 // check whether we have just received final sentence in list -- then enable interrupts
    {
      attachInterrupt(digitalPinToInterrupt(pinGPSSerIn), GetSerTime, FALLING);
      attachInterrupt(digitalPinToInterrupt(pinGPSPps), GetPPSTime, RISING);
      if (firstMessageSet)
      {
        firstMessageSet = false;
        digitalWriteFast(pinTest, HIGH);
//        Serial.print("Set pin");
//        Serial.print(pinTest);
//        Serial.print(" ");
//        Serial.println(HIGH);
      }
      else
      {
        gpsInfo.DecodeGGA(String(senStore[SENGGA]));
        gpsInfo.DecodeRMC(String(senStore[SENRMC]));

        if (!gpsInfo.CheckConsistency())
        {
          if (serialActive)
            Serial.println("inconsistent");
          if (sdActive)
          {
            logfile.print("inconsistent ");
            logfile.print(gpsInfo.GetGGATime());
            logfile.print(",");
            logfile.println(gpsInfo.GetRMCTime());
            logfile.flush();
          }
        }
        else
        {
          timeGPSStream_act = gpsInfo.GetTime();
          timeGPSStream_ard = serMilliLast;
          printTime(EncodeTime(timeGPSStream_act));
          UpdateFix(gpsInfo.CheckFix());
          UpdateSatNum(gpsInfo.GetSatNum());

          TimeEnc theTime = EncodeTime(timeGPSStream_act);
          int osCur = GetSatOffset(satNum);
          int osPrev = GetSatOffset(satNumPrev);
          int osUncert = GetSatUncert(satNum);

          if (!initialFilter)
          {
            double meas_t = double( (uint32_t((serMilliLast-osCur)*1000)-uint32_t(sec_xf[0]*1000))/1000L );    // deal with roll over
            //long pred_dt = sec_dxp-(osCur-osPrev);
            double pred_dt = sec_dxp;
            if (abs(pred_dt-meas_dt)>600)   // if there is a large diff. between prediction and measurement signals may have been missed. Restart filter to avoid errors
            {
              initialFilter = true;
              if (serialActive)
              {
                Serial.print("pred_meas error ");
                Serial.print(pred_dt);
                Serial.print(",");
                Serial.println(meas_dt);
              }
              if (sdActive)
              {
                logfile.print("pred_meas error ");
                logfile.print(pred_dt);
                logfile.print(",");
                logfile.println(meas_dt);
                logfile.flush();
              }
            }
            else
            {
                Serial.print("pred_meas ");
                Serial.print(pred_dt);
                Serial.print(",");
                Serial.print(meas_dt);
                Serial.print(",");
                Serial.println(secRem_xf);
                KalFilIter<float>(secRem_xf, float(pred_dt), meas_dt, sec_uf[0], sec_up, osUncert);
                Serial.println(secRem_xf);
            }
          }
          else                    // if this is the very first filter we have run we won't be able to use Kalman filter -- instead use signal time only
          {
            sec_xf[0] = serMilliLast-osCur;
            secRem_xf = 0;
            sec_uf[0] = osUncert;
            initialFilter = false;
          }
//          Serial.print("secRem_xf: ");
//          Serial.println(secRem_xf);
          
          sec_xf[0] = uint32_t(uint32_t(sec_xf[0]+int(secRem_xf))*1000)/1000L;
          secRem_xf -= int(secRem_xf);

          for (int i=1; i<PRED_NUM; i++)           // make next timing predictions
          {
            sec_xf[i] = (uint32_t(uint32_t(sec_xf[0]+sec_dxp*i)*1000))/1000L;
            sec_uf[i] = (uint32_t(uint32_t(sec_uf[0]+sec_up*i)*1000))/1000L;
          }
          pulseEstArmed = 1;

          Serial.println();
          Serial.print(serMilliLast);
          Serial.print(",");
          Serial.print(ppsMilliLast);
          Serial.print(",");
          Serial.print(sec_xf[0]);
          Serial.print(",");
          Serial.print(serMilliLast-ppsMilliLast);
          Serial.print(",");
          Serial.print(serMilliLast-sec_xf[0]);
          Serial.print(",");
          Serial.println(satNum);
          

          // Write to SD card
          if (sdActive)
          {
            logfile.print(serMilliLast);
            logfile.print(",");
            logfile.print(ppsMilliLast);
            logfile.print(",");
            logfile.print(sec_xf[0]);
            logfile.print(",");
            logfile.println(satNum);
            logfile.flush();
          }

          // Apply a second Kalman filter
        }
      }
      //serTEndLast = millis();
    }
    if (firstNonLoop && !reading)
    {
      firstNonLoop = false;
      firstLoop = true;
    }
  }
}

void UpdateInput()
{
  bRes.UpdateState();
}

void UpdateOutput()
{
  if (bRes.GetState() == 1)     // Reset if reset button is pressed
    WRITE_RESTART(0x5FA0004);

  lcd.SetText(0, 0, String(int(millis() / 50) * 50));
  lcd.Update();

  String dataGPStr = String(senStore[senNum]);
  if (dataGPStr.length() > 16)
    lcd.SetText(0, 1, dataGPStr.substring(0, 16));
}


void GetSerTime() {
  serMilli = double(myMicros)/1000L;
  uint32_t serMilli_Dif = (uint32_t(serMilli*1000)-uint32_t(serMilli_*1000))/1000;
  uint32_t serMilliLastDif = (uint32_t(serMilli*1000)-uint32_t(serMilliLast*1000))/1000;
  if (serMilliLastDif>250 && (serMilli_Dif>200)) {
    serMilliLast = serMilli;
    Serial.print("Ser at ");
    Serial.println(serMilliLast);
  }
  serMilli_ = serMilli;
}

void GetPPSTime() {
  ppsMilli = double(myMicros)/1000L;
  if (ppsMilli > ppsMilliLast+250) {
    ppsMilliLast = ppsMilli;
    Serial.print("Pps at ");
    Serial.println(serMilliLast);
  }
}

void CheckSecondTurn()
{
  if (!ppsEmit && !initialFilter)      // check whether we are currently emitting
  {
    unsigned long timeCur = myMicros/1000;
    float predTimeAfterDif = int32_t(uint32_t(sec_xf[PRED_NUM-1]*1000)-uint32_t(timeCur*1000))/1000;
    float predTimeThisDif = int32_t(uint32_t(sec_xf[pulseEstArmed]*1000)-uint32_t(timeCur*1000))/1000;
    if (predTimeAfterDif<=0) // check whether the last predicted second has turned (if so the Kalman filter wasn't called -- something wrong with message)
    {
      Serial.println();
      Serial.print("~~Missed second! ");
      Serial.print(timeCur);
      Serial.print(", ");
      Serial.print(sec_xf[0]);
      Serial.print(", ");
      Serial.println(sec_xf[1]);
      EmitPPS(true);
      // shift the next second's prediction into the current second, and use the expected second length to predict the next second
      sec_xf[0] = sec_xf[1];
      sec_uf[0] = sec_uf[0];
      sec_xf[1] = sec_xf[0]+sec_dxp;
      sec_uf[1] = sec_xf[0]+sec_up;
      pulseEstArmed = PRED_NUM-1;
    }
    else if (predTimeThisDif<=0)  // check whether the current second has turned
    {
      Serial.print("Start emit at ");
      Serial.print(timeCur);
      Serial.print(",  sec_xf[1] at ");
      Serial.print(sec_xf[1]);
      Serial.print(";   ");
      Serial.print(predTimeAfterDif);
      Serial.print(", ");
      Serial.println(predTimeThisDif);
      EmitPPS(true);
    }
  }
  else                              // else we are emitting; we must check whether to stop emitting
  {
    if (pulseTimer.Check())
      EmitPPS(false);
  }
}

void EmitPPS(bool emit)
{
  if (serialActive)
  {
    Serial.print("Emit ");
    Serial.print(emit);
    Serial.print(" time ");
    Serial.println(millis());
  }
  
  ppsEmit = emit;
  digitalWriteFast(pinLedPps, ppsEmit);
  digitalWriteFast(pinPpsOut, ppsEmit);
  if (emit)
  {
    pulseTimer.Start();
    pulseEstArmed++;
  }
  else
    pulseTimer.Reset();
}

void UpdateFix(bool fix_)
{
  if (fix!=fix_)
    digitalWriteFast(pinLedFix, fix_);
  fix = fix_;
}

void UpdateSatNum(byte satNum_)
{
  satNumPrev = satNum;
  satNum = satNum_;
}

int GetSatOffset(byte satNum)
{
  if (satNum>=SATDATA_NUM)
    satNum = SATDATA_NUM-1;
  return satOffsets[satNum];
}

int GetSatUncert(byte satNum)
{
  if (satNum>=SATDATA_NUM)
    satNum = SATDATA_NUM-1;
  return satUncerts[satNum];
}

void printTime(TimeEnc t)
{
  Serial.print(t.h);
  Serial.print(":");
  Serial.print(t.m);
  Serial.print(":");
  Serial.print(t.s);
  Serial.print(":");
  Serial.print(t.ms);

  Serial.print(";  ");
  Serial.println(DecodeTime(t));
}
