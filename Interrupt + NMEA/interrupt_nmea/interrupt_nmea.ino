#include <SPI.h>
#include <SoftwareSerial.h>
#include "SdFat.h"
#include <avr/sleep.h>

SoftwareSerial gpsSerial(8, 7);


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
char nmea1[90];
char nmea2[90];
bool writeData = false;
bool firstLoop = true;
int fill = 1;

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

void setup() {
  pinMode(ledPin, OUTPUT);

  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);

  Blink(ledPin, 1500);

  if (!sd.begin(chipSelect, SPI_FULL_SPEED)) {      // if you're using an UNO, you can use this line instead
    error(2);
  }
  char filename[15];
  strcpy(filename, "GPSMIL00.TXT");
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

  // Start the software serial connection
  gpsSerial.begin(9600);

  pinMode(3, INPUT);
  pinMode(2, INPUT);
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
}

void loop() {
  while(gpsSerial.available()) {

    // If this is the first time we've entered the loop, remove the interrupts so our serial reading isn't interrupted.
    if (firstLoop) {
      detachInterrupt(digitalPinToInterrupt(2));
      detachInterrupt(digitalPinToInterrupt(3));
    }

    // Read from the software serial buffer
    char c = gpsSerial.read();

    // We want to record two NMEA sentences. So start by filling nmea1 buffer...
    if (fill == 1) {
      nmea1[count1] = c;
      count1++;
      if (c == '\n') {
        nmea1[count1] = '\0';
        fill = 2;
      }
    // Then fill the nmea2 buffer.
    } else if (fill == 2) {
      nmea2[count2] = c;
      count2++;
      if (c == '\n') {
        nmea2[count2] = '\0';
        fill = 1;

        // Once we've got both sentences, set our write flag to true and exit the loop
        writeData = true;
        break;
      }
    }
  }
  
  if (writeData == true) {
    // Write NMEA sentences to file
    logfile.print(nmea1);
    logfile.print(nmea2);

    // Write the serial and PPS interrupt trigger times too
    logfile.print("t");
    logfile.print(milliLast);
    logfile.print(",");
    logfile.println(ppsMilliLast);

    // Force a file write
    logfile.flush();
    
    // Reset for next data set
    nmea1[0] = (char)0;
    nmea2[0] = (char)0;
    count1 = 0;
    count2 = 0;
    writeData = false;

    // Re-attach the interrupts we removed earlier
    attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
    attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
  }
}

void getInputTime() {
  milli = millis();
  dt = milli - milliLast;
  if(dt > 200) {
    milliLast = milli;
  }
}

void getPPSTime() {
  ppsMilli = millis();
  ppsDt = ppsMilli - ppsMilliLast;
  if(ppsDt > 200) {
    ppsMilliLast = ppsMilli;
  }
}

/* End code */

