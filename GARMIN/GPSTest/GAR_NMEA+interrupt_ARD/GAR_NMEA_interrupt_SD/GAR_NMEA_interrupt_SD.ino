#include <AltSoftSerial.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include "SdFat.h"

byte pinRX = 2;
byte pinTX = 4;
byte pinPPS = 3;

int boadCur = 9600;
#define chipSelect 10
#define ledPin 13

SdFat sd;
SdFile logfile;

SoftwareSerial gps(pinRX, pinTX, true);

char dataByte = 0;
byte sentenceNum = 2;
char* sentencePrefixTerm = "$GPGGA";    // this sentence is the last one in the list
char* sentencePrefixRMC = "$GPRMC";
char* sentencePrefixGGA = "$GPGGA";
char* sentencePrefixArr[2] = {sentencePrefixRMC, sentencePrefixGGA};

char dataGP[85];
unsigned char dataPos;
bool willSend = false;
byte senLast = 0; // most recent sentence type to be identified

volatile uint32_t serTEndLast = millis();           // used to fix error which caused ppsser time to be ~500 rather than ~400 ms (serial interrupt may have caught end of message?)
volatile uint32_t serTLast = millis();
volatile uint32_t serDt = 0;
volatile uint32_t serMilli = millis();
volatile uint32_t serMilliLast = millis();
volatile uint32_t ppsDt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();
bool firstNonLoop = false;
bool firstLoop = true;
bool firstMessageSet = true;                       // don't send the first one -- usually wrong
bool reading = true;
bool senTerm = false;



// blink out an error code
void error(uint8_t errno) {           // note: blink code won't work after sd.begin() because SPI disables pin13 LED!!! We must end SPI first
  SPI.end();
  while(1) {
    uint8_t i;
    for (i=0; i<errno; i++) {
      Blink(ledPin, 100);
    }
    for (i=errno; i<10; i++) {
      delay(200);
    }
  }
}

void Blink(byte pin, int t)
{
  for (byte k=0; k<2; k++)
  {
    digitalWrite(pin, k);
    delay(t);
  }
}

void setup()
{
  pinMode(pinRX, INPUT);
  pinMode(pinTX, OUTPUT);
  pinMode(pinPPS, INPUT);

  dataPos = 0;
  pinMode(ledPin, OUTPUT);
  pinMode(chipSelect, OUTPUT);

  if (!sd.begin(chipSelect, SPI_FULL_SPEED)) {      // if you're using an UNO, you can use this line instead
    error(2);
  }
  char filename[16];
  strcpy(filename, "GPSNMEA00.TXT");
  for (uint8_t i = 0; i < 100; i++) {
    filename[7] = '0' + i/10;
    filename[8] = '0' + i%10;
    // create if does not exist, do not open existing, write, sync after write
    if (! sd.exists(filename)) {
      break;
    }
  }

  if (!logfile.open(filename, O_RDWR | O_CREAT | O_AT_END)) {
    error(3);
  }
  logfile.flush();

  Serial.begin(9600);
  
  gps.begin(boadCur);
}

void loop()
{  
  if (gps.available())
  {
    reading = true;
//    if (dataPos == 0)
//    {
//      serMilliLast = millis();
//    }
    // If this is the first time we've entered the loop, remove the interrupts so our serial reading isn't interrupted.
    if (firstLoop)
    {
      detachInterrupt(digitalPinToInterrupt(pinRX));
      detachInterrupt(digitalPinToInterrupt(pinPPS));
      firstNonLoop = true;
      firstLoop = false;
    }
    volatile uint32_t serTCur = millis();
    dataByte = char(gps.read());
    if (dataByte == 0xD)      // check for end of sentence
    {
      while (dataByte != 0xA)
        dataByte = gps.read();

      if (willSend)
      {
        dataGP[dataPos] = '\n';
        dataGP[dataPos+1] = '\0';
        willSend = false;

        logfile.print(dataGP);
      }
      dataPos = 0;
      reading = false;
    }
    if (reading)
    {
      if (dataPos<pow(2,sizeof(dataPos)*8)-3)
      {
        dataGP[dataPos] = dataByte;
        dataPos++;
      }
      if (dataPos==7)
      {
        for (byte senType=0; senType<sentenceNum; senType++)
        {
          willSend = true;
          for (byte i=0; i<6; i++)
            willSend = willSend&(sentencePrefixArr[senType][i]==dataGP[i]);
          if (willSend)
          {
            senLast = senType;
            break;
          }
        }
        // check whether we have the terminal sentence
        senTerm = true;
        for (byte i=0; i<6; i++)
          senTerm = senTerm&(sentencePrefixTerm[i]==dataGP[i]);                                                                                                                                                                                                                                                            
      }
    }
  }
          // else: serial not available
  {
    if (firstNonLoop && !reading && senTerm)                 // check whether we have just received final sentence in list -- then enable interrupts
    {
      if (firstMessageSet)
        firstMessageSet = false;
      else
      {
        logfile.print('t');
        logfile.print(serMilliLast);
        logfile.print(',');
        logfile.print(ppsMilliLast);
        logfile.print("\n");
        logfile.flush();
      }
    }
    if (firstNonLoop && !reading)
    {
      attachInterrupt(digitalPinToInterrupt(pinRX), getSerTime, RISING);
      attachInterrupt(digitalPinToInterrupt(pinPPS), getPPSTime, RISING);
      firstNonLoop = false;
      firstLoop = true;
    }
  }
}

void getSerTime() {
  serMilli = millis();
  serDt = serMilli - serMilliLast;
  if(serDt > 250 && serMilli-serTEndLast>20) {
    serMilliLast = serMilli;
  }
}

void getPPSTime() {
  ppsMilli = millis();
  ppsDt = ppsMilli - ppsMilliLast;
  if(ppsDt > 250) {
    ppsMilliLast = ppsMilli;
  }
}

