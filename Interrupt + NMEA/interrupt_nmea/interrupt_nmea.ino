#include <SPI.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
//#include <SD.h>
#include <SdFat.h>

#include <avr/sleep.h>

SoftwareSerial gpsSerial(8, 7);
Adafruit_GPS GPS(&gpsSerial);

// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO  true
/* set to true to only log to SD when GPS has a fix, for debugging, keep it false */
#define LOG_FIXONLY false  

// Set the pins used
#define chipSelect 10
#define ledPin 13

SdFat sd;
SdFile logfile;

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();
volatile uint32_t ppsDt = 0;
int writeNow = 0;
int ppsWriteNow = 0;
int count1 = 0;
int count2 = 0;
char nmea1[80];
char nmea2[80];


// read a Hex value and return the decimal equivalent
uint8_t parseHex(char c) {
  if (c < '0')
    return 0;
  if (c <= '9')
    return c - '0';
  if (c < 'A')
    return 0;
  if (c <= 'F')
    return (c - 'A')+10;
}

// blink out an error code
void error(uint8_t errno) {
  /*
  if (SD.errorCode()) {
   putstring("SD error: ");
   Serial.print(card.errorCode(), HEX);
   Serial.print(',');
   Serial.println(card.errorData(), HEX);
   }
   */
  while(1) {
    uint8_t i;
    for (i=0; i<errno; i++) {
      digitalWrite(ledPin, HIGH);
      delay(100);
      digitalWrite(ledPin, LOW);
      delay(100);
    }
    for (i=errno; i<10; i++) {
      delay(200);
    }
  }
}

void setup() {
  pinMode(ledPin, OUTPUT);

  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);

  if (!sd.begin(chipSelect)) {      // if you're using an UNO, you can use this line instead
    error(2);
  }
  char filename[15];
  strcpy(filename, "GPSLOG00.TXT");
  for (uint8_t i = 0; i < 100; i++) {
    filename[6] = '0' + i/10;
    filename[7] = '0' + i%10;
    // create if does not exist, do not open existing, write, sync after write
    if (! sd.exists(filename)) {
      break;
    }
  }

  if (!logfile.open(filename, O_RDWR | O_CREAT | O_AT_END)) {
    error(3);
  }

  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  GPS.sendCommand(PGCMD_NOANTENNA);

  pinMode(3, INPUT);
  pinMode(2, INPUT);
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
}

void loop() {
  char c = GPS.read();
  detachInterrupt(digitalPinToInterrupt(2));
  detachInterrupt(digitalPinToInterrupt(3));
  while (c) {
    if (count2) {
      nmea1[count1] = c;
      count1++;
      if (c == '\n') {
        nmea1[count1] = '\0';

      }
    } else {
      nmea2[count2] = c;
      count2++;
      if (c == '\n') {
        nmea2[count2] = '\0';
        
      }
    }
    c = GPS.read();
  }

  // Write to file
  logfile.print(nmea1);
  logfile.print(",");
  logfile.print(milliLast);
  logfile.print(",");
  logfile.println(ppsMilliLast);
  logfile.print(nmea2);
  logfile.print(",");
  logfile.print(milliLast);
  logfile.print(",");
  logfile.println(ppsMilliLast);
  logfile << flush;
  
  // Reset for next data set
  nmea1[0] = (char)0;
  nmea2[0] = (char)0;
  count1 = 0;
  count2 = 0;
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
}

void getInputTime() {
  milli = millis();
  dt = milli - milliLast;
  if(dt > 200) {
    milliLast = milli;
    writeNow = 1;
  }
}

void getPPSTime() {
  ppsMilli = millis();
  ppsDt = ppsMilli - ppsMilliLast;
  if(ppsDt > 200) {
    ppsMilliLast = ppsMilli;
    if(writeNow) {
      // We want the PPS time THEN the serial time, not the other way around
      writeNow = 0;
    } 
    ppsWriteNow = 1;
  }
}

/* End code */

