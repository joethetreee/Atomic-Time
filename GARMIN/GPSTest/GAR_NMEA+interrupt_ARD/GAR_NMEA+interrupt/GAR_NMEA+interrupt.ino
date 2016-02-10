#include <AltSoftSerial.h>
#include <SoftwareSerial.h>

byte pinRX = 2;
byte pinTX = 4;
byte pinPPS = 3;

SoftwareSerial gps(pinRX,pinTX,true);
//AltSoftSerial gps(pinRX,pinTX,true);
unsigned char dataByte;
int boadCur = 9600;


byte sentenceNum = 2;
char* sentencePrefixTerm = "$GPGGA";    // this sentence is the last one in the list
char* sentencePrefixRMC = "$GPRMC";
char* sentencePrefixGGA = "$GPGGA";
char* sentencePrefixArr[2] = {sentencePrefixRMC, sentencePrefixGGA};

char dataGP[85];
unsigned char dataPos;
bool willSend = false;
byte senLast = 0; // most recent sentence type to be identified

volatile uint32_t serTLast = millis();
volatile uint32_t serDt = 0;
volatile uint32_t serMilli = millis();
volatile uint32_t serMilliLast = millis();
volatile uint32_t ppsDt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();
bool firstNonLoop = false;
bool firstLoop = true;
bool reading = true;
bool senTerm = false;



void setup()
{
  pinMode(pinRX, INPUT);
  pinMode(pinTX, OUTPUT);
  pinMode(pinPPS, INPUT);
  gps.begin(boadCur);
  Serial.begin(9600);
  dataPos = 0;
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

        Serial.print(dataGP);
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
      Serial.print('t');
      Serial.print(serMilliLast);
      Serial.print(',');
      Serial.print(ppsMilliLast);
      Serial.print("\n");
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
  if(serDt > 50) {
    serMilliLast = serMilli;
  }
}

void getPPSTime() {
  ppsMilli = millis();
  ppsDt = ppsMilli - ppsMilliLast;
  if(ppsDt > 50) {
    ppsMilliLast = ppsMilli;
  }
}
