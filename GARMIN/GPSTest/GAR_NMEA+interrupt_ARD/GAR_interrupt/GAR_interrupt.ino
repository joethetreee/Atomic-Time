#include <AltSoftSerial.h>
#include <SoftwareSerial.h>

byte pinRX = 2;
byte pinTX = 4;
byte pinPPS = 3;

byte sentenceNum = 2;
char* sentencePrefixTerm = "$GPGGA";    // this sentence is the last one in the list
char* sentencePrefixRMC = "$GPRMC";
char* sentencePrefixGGA = "$GPGGA";
char* sentencePrefixArr[2] = {sentencePrefixRMC, sentencePrefixGGA};

char dataGP[85];
unsigned char dataPos;
bool willSend = false;
byte senLast = 0; // most recent sentence type to be identified

volatile uint32_t serMilliLast = millis();
volatile uint32_t serDt = 0;
volatile uint32_t serMilli = millis();
volatile uint32_t ppsDt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();

byte modeSer = 2;         // 0: wait for serial; 1: wait for PPS; If values +2, must disable the other interrupt
int waitTime = 500;       // time in ms to wait after interrupts before possibly enabling it



void setup()
{
  pinMode(pinRX, INPUT);
  pinMode(pinTX, OUTPUT);
  pinMode(pinPPS, INPUT);
  Serial.begin(9600);
}

void loop()
{  
  if (millis()-ppsMilliLast > waitTime && modeSer==2)
  {
    attachInterrupt(digitalPinToInterrupt(pinPPS), getPPSTime, RISING);
    modeSer=0;
  }

  if (modeSer==3 )              // if waiting for Serial and we have just detected PPS (then modeSer>=2; must detach interrupt)
  {
    detachInterrupt(digitalPinToInterrupt(pinPPS));
    attachInterrupt(digitalPinToInterrupt(pinRX), getSerTime, RISING);
    modeSer = 1;
  }
  if (modeSer==4)                 // if we have just received serial; then we can transmit data
  {
    modeSer = 2;
    Serial.print('t');
    Serial.print(serMilliLast);
    Serial.print(',');
    Serial.print(ppsMilliLast);
    Serial.print("\n");
    detachInterrupt(digitalPinToInterrupt(pinRX));
  }
}

void getPPSTime() {
  ppsMilli = millis();
  ppsDt = ppsMilli - ppsMilliLast;
  if(ppsDt > 250) {
    ppsMilliLast = ppsMilli;
    modeSer = 3;
  }
}

void getSerTime() {
  serMilli = millis();
  serDt = serMilli - serMilliLast;
  if(serDt > 250) {
    serMilliLast = serMilli;
    modeSer = 4;
  }
}
