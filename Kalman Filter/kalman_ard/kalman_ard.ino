// Kalman_ard.ino
// Author: Joe Wilson
// Created: 10/02/2016

// _SS_MAX_RX_BUFF in SoftwareSerial.h was changed to 256.

#include <SPI.h>
#include <SoftwareSerial.h>
#include <avr/sleep.h>
#include "SdFat.h"

#define ppsOutPin 5
#define chipSelect 10

SoftwareSerial gpsSerial(8, 7);

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();
volatile uint32_t ppsDt = 0;
bool firstLoop = true;
bool firstSer = true;
bool outPPSStart = false;
bool outPPSEnd = false;

// NMEA Parsing
int fill = 1;
int count1 = 0;
int count2 = 0;
char nmea1[90];
char nmea2[90];
char nmeaTime[11];
char nmeaTime500[11];
char numSatsChar[3];
int numSats = 0;
int satOffsets[13] = {0, 0, 0, 224, 233, 245, 262, 281, 294, 304, 320, 303, 330}; // PPS Distribution Offset Average from
                                                                                // kalman_ard.py on GPSMIL37ChckdCor.txt dataset

// SD Card
SdFat sd;
SdFile logfile;


// Kalman filter variables (multipled by 100 for decimal precision using integer arithmetic in filterStep())
unsigned long arduinoUncertainty = 100;
unsigned long gpsUncertainty = 50000;
unsigned long arduinoSecond = 100100;

unsigned long A = 1;
unsigned long B = 1;
unsigned long H = 1;
unsigned long Q = arduinoUncertainty;
unsigned long R = gpsUncertainty;

unsigned long currentStateEstimate;
unsigned long currentStateEstimateULong500;
unsigned long currentStateEstimateULong600;
unsigned long currentProbEstimate = gpsUncertainty;
int innovation;
unsigned long innovationCovariance;
float kalmanGain;
unsigned long predictedStateEstimate;
unsigned long predictedProbEstimate;

bool stepKalman = false;

// Main program
void setup() {
  Serial.begin(115200);
  Serial.println("Kalman Filter 0.2");

  // Chip select
  pinMode(chipSelect, OUTPUT);

  if (!sd.begin(chipSelect, SPI_FULL_SPEED)) {      // if you're using an UNO, you can use this line instead
    Serial.println("Error 2");
  }
  char filename[15];
  strcpy(filename, "KL2PPS00.TXT");
  for (uint8_t i = 0; i < 100; i++) {
    filename[6] = '0' + i/10;
    filename[7] = '0' + i%10;
    // create if does not exist, do not open existing, write, sync after write
    if (! sd.exists(filename)) {
      break;
    }
  }
  if (!logfile.open(filename, O_RDWR | O_CREAT | O_AT_END)) {
    Serial.println("Error 3");
  }

  // Setup Timer0 to call our once-per-millisecond function.
  OCR0A = 0xAF;
  TIMSK0 |= _BV(OCIE0A);

  // Start the software serial connection
  gpsSerial.begin(9600);

  delay(2000);
  gpsSerial.flush();

  pinMode(3, INPUT);
  pinMode(ppsOutPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
  
  pinMode(2, INPUT);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
}


void loop() {
  if(stepKalman) {
    if (firstSer) {
      currentStateEstimate = milliLast * 100;
      firstSer = false;
      stepKalman = false;
    } else  {
      stepKalman = false;
      filterStep(1000, milliLast - satOffsets[numSats]);
      outPPSStart = false;

      // Write to SD card
      logfile.print(currentStateEstimateULong500);
      logfile.print(",");
      logfile.print(ppsMilliLast);
      logfile.print(",");
      logfile.print(milliLast);
      logfile.print(",");
      logfile.println(numSats);
      logfile.flush();

      /*
      Serial.print(currentStateEstimateULong500);
      Serial.print(",");
      Serial.print(milliLast);
      Serial.print(",");
      Serial.print(numSats);
      Serial.print(",");
      Serial.println(currentStateEstimate);
      */
    }
  }
  
  while(gpsSerial.available()) {

    // If this is the first time we've entered the loop, remove the interrupts so our serial reading isn't interrupted.
    if (firstLoop) {
      detachInterrupt(digitalPinToInterrupt(3));
      firstLoop = false;
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

        // Is this GGA?
        if(nmea1[3] == 'G') {
          int pos1 = strpos(nmea1,',', 7);
          int pos2 = strpos(nmea1, ',', 8);

          if(pos1 != -1 && pos2 != -1) {
            numSatsChar[0] = '\0';
            strncpy(numSatsChar, nmea1 + pos1 + 1, pos2 - pos1 - 1);
            numSatsChar[pos2 - pos1 - 1] = '\0';
            numSats = atoi(numSatsChar);
          }
        }
      }
    // Then fill the nmea2 buffer.
    } else if (fill == 2) {

      nmea2[count2] = c;
      count2++;
      if (c == '\n') {

        nmea2[count2] = '\0';
        fill = 1;

        nmeaTime[0] = '\0';
        strncpy(nmeaTime, nmea2 + 7, 10);
        nmeaTime[10] = '\0';

        // Create a copy of the NMEA timestamp
        strcpy(nmeaTime500, nmeaTime);
        // Add the 500ms offset
        nmeaTime500[7] = '5';

        // Is this GGA?
        if(nmea2[3] == 'G') {
          int pos1 = strpos(nmea2,',', 7);
          int pos2 = strpos(nmea2, ',', 8);

          if(pos1 != -1 && pos2 != -1) {
            numSatsChar[0] = '\0';
            strncpy(numSatsChar, nmea2 + pos1 + 1, pos2 - pos1 - 1);
            numSatsChar[pos2 - pos1 - 1] = '\0';
            numSats = atoi(numSatsChar);
          }
        }

        count1 = 0;
        count2 = 0;
        nmea1[0] = '\0';
        nmea2[0] = '\0';
        firstLoop = true;

        // Once we've got both sentences, set our write flag to true and exit the loop
        attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
        break;
      }
    }
  }
}

void getInputTime() {
  milli = millis();
  dt = milli - milliLast;
  if(dt > 500) {
    milliLast = milli;
    stepKalman = true;
  }
}

void getPPSTime() {
  ppsMilli = millis();
  ppsDt = ppsMilli - ppsMilliLast;
  if(ppsDt > 500) {
    ppsMilliLast = ppsMilli;
  }
}

void filterStep(unsigned long controlVector, unsigned long measurementVector) {
  // Prediction
  // We multiply by 100 to have 2 decimal place precision whilst using integer arithmetic.
  predictedStateEstimate = A * currentStateEstimate + B * (controlVector * 100);
  predictedProbEstimate = A * currentProbEstimate * A + Q;

  // Observation
  innovation = (measurementVector * 100) - H * predictedStateEstimate;
  innovationCovariance = H * predictedProbEstimate * H + R;

  // Update
  kalmanGain = (float)(predictedProbEstimate * H) / innovationCovariance;
  currentStateEstimate = predictedStateEstimate + kalmanGain * innovation;
  currentProbEstimate = (1.0 - kalmanGain * H) * predictedProbEstimate;

  // Converts back to milliseconds and adds 500 milliseconds to allow for signals
  // arriving late.
  currentStateEstimateULong500 = currentStateEstimate / 100 + 500;
  currentStateEstimateULong600 = currentStateEstimateULong500 + 100;
}

// Function called once per millisecond
SIGNAL(TIMER0_COMPA_vect) {
  unsigned long tempMillis = millis();
  if(outPPSStart == false) {
    if(tempMillis >= currentStateEstimateULong500) {
      outPPSStart = true;
      outPPSEnd = false;
      digitalWrite(ppsOutPin, HIGH); // PPS on
    }
  } else if(outPPSEnd == false) {
    if(tempMillis >= currentStateEstimateULong600) {
      outPPSEnd = true;
      digitalWrite(ppsOutPin, LOW); // PPS off
    }
  }
}

// Finds the nth occurance of a character in a string. Returns -1 if not found.
int strpos(char* haystack, char needle, int nth) {
  int counter = 0;
  for(int i = 0; i <= strlen(haystack); i++) {
    if(haystack[i] == needle) {
      counter += 1;
      if(counter == nth) {
        return i;
      }
    }
  }
  return -1;
}
