// Kalman_ard.ino
// Author: Joe Wilson
// Created: 10/02/2016

#include <SPI.h>
#include <avr/sleep.h>

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
bool firstLoop = true;
bool firstSer = true;
bool sent = false;

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
unsigned long currentStateEstimateULong;
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

  pinMode(3, INPUT);
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
      sent = false;
      /*Serial.print(milliLast);
      Serial.print(" ");
      Serial.print(currentStateEstimateULong);
      Serial.print(" ");
      Serial.print(currentProbEstimate);
      Serial.print(" ");*/
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

  currentStateEstimateULong = (unsigned long)(currentStateEstimate + 0.5) + 500;
}

// Function called once per millisecond
SIGNAL(TIMER0_COMPA_vect) {
  if(sent == false) {
    if(millis() >= currentStateEstimateULong) {
      sent = true;
      Serial.print(millis() - currentStateEstimateULong);
      Serial.print(" ");
      Serial.print(currentStateEstimateULong);
      Serial.print(" ");
      Serial.println(currentStateEstimateULong >= milliLast); 
    }
  }
}
