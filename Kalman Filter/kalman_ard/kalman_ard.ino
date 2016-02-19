// Kalman_ard.ino
// Author: Joe Wilson
// Created: 10/02/2016

#include <SPI.h>
#include <SoftwareSerial.h>
#include <avr/sleep.h>

#define ppsOutPin 5

SoftwareSerial gpsSerial(8, 7);

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
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
char nmeaTime[12];

// Kalman filter variables
unsigned long arduinoUncertainty = 1;
unsigned long gpsUncertainty = 500;
unsigned long arduinoSecond = 1001;

unsigned long A = 1;
unsigned long B = 1;
unsigned long H = 1;
unsigned long Q = 1;
unsigned long R = arduinoUncertainty + gpsUncertainty;

float currentStateEstimate;
unsigned long currentStateEstimateULong500;
unsigned long currentStateEstimateULong600;
float currentProbEstimate = gpsUncertainty;
float innovation;
float innovationCovariance;
float kalmanGain;
float predictedStateEstimate;
float predictedProbEstimate;

bool stepKalman = false;

// Main program
void setup() {
  Serial.begin(9600);
  Serial.println("Kalman Filter 0.1");

  // Setup Timer0 to call our once-per-millisecond function.
  OCR0A = 0xAF;
  TIMSK0 |= _BV(OCIE0A);

  // Start the software serial connection
  gpsSerial.begin(9600);

  pinMode(3, INPUT);
  pinMode(ppsOutPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
}


void loop() {
  if(stepKalman) {
    if (firstSer) {
      currentStateEstimate = milliLast;
      firstSer = false;
      stepKalman = false;
      //Serial.println(milliLast);
    }
    else  {
      stepKalman = false;
      filterStep(1000, milliLast);
      outPPSStart = false;
      /*Serial.print(milliLast);
      Serial.print(" ");
      Serial.print(currentStateEstimateULong);
      Serial.print(" ");
      Serial.print(currentProbEstimate);
      Serial.print(" ");*/
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
       // Serial.println(nmeaTime);

        count1 = 0;
        count2 = 0;
        nmea1[0] = '\0';
        nmea2[0] = '\0';

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

void filterStep(int controlVector, unsigned long measurementVector) {
  // Prediction
  predictedStateEstimate = A * currentStateEstimate + B * controlVector;
  predictedProbEstimate = A * currentProbEstimate * A + Q;

  // Observation
  innovation = measurementVector - H * predictedStateEstimate;
  innovationCovariance = H * predictedProbEstimate * H + R;

  // Update
  kalmanGain = predictedProbEstimate * H / innovationCovariance;
  currentStateEstimate = predictedStateEstimate + kalmanGain * innovation;
  currentProbEstimate = (1 - kalmanGain * H) * predictedProbEstimate;

  // Converts the state estimate to a unsigned long and adds 500 milliseconds to allow for signals
  // arriving late.
  currentStateEstimateULong500 = (unsigned long)(currentStateEstimate + 0.5) + 500;
  currentStateEstimateULong600 = currentStateEstimateULong500 + 100;
}

// Function called once per millisecond
SIGNAL(TIMER0_COMPA_vect) {
  if(outPPSStart == false) {
    if(millis() >= currentStateEstimateULong500) {
      outPPSStart = true;
      outPPSEnd = false;
      digitalWrite(ppsOutPin, HIGH);
      Serial.print(millis() - currentStateEstimateULong500);
      Serial.print(" ");
      Serial.print(currentStateEstimateULong500);
      Serial.print(" ");
      Serial.println(currentProbEstimate);
    }
  }

  if(outPPSEnd == false) {
    if(millis() >= currentStateEstimateULong600) {
      outPPSEnd = true;
      digitalWrite(ppsOutPin, LOW);
    }
  }
}
