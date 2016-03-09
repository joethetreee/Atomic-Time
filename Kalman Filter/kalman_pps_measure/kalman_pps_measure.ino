// Kalman_pps_measure.ino
// Author: Joe Wilson
// Created: 23/02/2016
// Measures the time offset between GPS PPS and Kalman PPS
// on second Arduino board. Saves to SD card.

#include <SPI.h>
#include "SdFat.h"

// Set the pins used
#define chipSelect 4
#define ledPin 13

SdFat sd;
SdFile logfile;

volatile uint32_t kalMilli = millis();
volatile uint32_t kalMilliLast = millis();
volatile uint32_t kalDt = 0;
volatile bool writeKal = false;
volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
volatile bool writePPS = false;

// blink out an error code
void error(uint8_t errno) {           // note: blink code won't work after sd.begin() because SPI disables pin13 LED!!! We must end SPI first
  SPI.end();
  Serial.println(errno);
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

void Blink(byte pin, int t) {
  for (byte k=0; k<2; k++)
  {
    digitalWrite(pin, k);
    delay(t);
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(ledPin, OUTPUT);

  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);
  
  if (!sd.begin(chipSelect, SPI_HALF_SPEED)) {      // if you're using an UNO, you can use this line instead
    error(2);
  }
  char filename[15];
  strcpy(filename, "KALPPS00.TXT");
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

  // Attached interrupts to digital input pins 2 and 3.
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
  attachInterrupt(digitalPinToInterrupt(3), getKalPPSTime, RISING);

  // Welcome message
  Serial.println("Kalman Diagnostics");
  Serial.println("Saving to " + String(filename) + "\n");
  Serial.println("Kalman PPS | GPS PPS");
}

void loop() {
  if(writeKal && writePPS) {
    // Output over serial
    Serial.print(kalMilliLast);
    Serial.print(" | ");
    Serial.println(milliLast);

    // Save to SD card
    logfile.print(kalMilliLast);
    logfile.print(",");
    logfile.println(milliLast);

    logfile.flush();

    // We've written the data
    writeKal = false;
    writePPS = false;
  }
}

void getKalPPSTime() {
  kalMilli = millis();
  kalDt = kalMilli - kalMilliLast;
  if(kalDt > 200) {
    kalMilliLast = kalMilli;
    writeKal = true;
  }
}

void getPPSTime() {
  milli = millis();
  dt = milli - milliLast;
  if(dt > 200) {
    milliLast = milli;
    writePPS = true;
  }
}
