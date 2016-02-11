#include <SPI.h>
#include <SoftwareSerial.h>
#include <avr/sleep.h>

SoftwareSerial gpsSerial(8, 7);


// Set the pins used
#define ledPin 13

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();
volatile uint32_t ppsDt = 0;
int writeNow = 0;
int ppsWriteNow = 0;
bool dataEnd = false;
bool firstLoop = true;
int fill = 1;

// Kalman filter variables
int arduinoUncertainty = 1;
int gpsUncertainty = 500;
int arduinoSecond = 1001;

int A = 1;
int B = 1;
int H = 1;
int Q = 1;
int R = arduinoUncertainty + gpsUncertainty;

unsigned long currentStateEstimate;
unsigned long currentProbEstimate = arduinoUncertainty;
float innovation;
float innovationCovariance;
float kalmanGain;
float predictedStateEstimate;
float predictedProbEstimate;

bool stepKalman = false;

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
  Serial.begin(9600);
  Serial.println("Kalman Filter 0.1");
  
  pinMode(ledPin, OUTPUT);
  Blink(ledPin, 1500);

  // Start the software serial connection
  gpsSerial.begin(9600);

  pinMode(3, INPUT);
  pinMode(2, INPUT);
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
}

void loop() {
  if(stepKalman) {
    stepKalman = false;
    filterStep(1000, milliLast);
    Serial.print(milliLast);
    Serial.print(" ");
    Serial.println(currentStateEstimate);
  }
  
  while(gpsSerial.available()) {

    // If this is the first time we've entered the loop, remove the interrupts so our serial reading isn't interrupted.
    if (firstLoop) {
      detachInterrupt(digitalPinToInterrupt(2));
      detachInterrupt(digitalPinToInterrupt(3));
      firstLoop = false;
    }

    // Read from the software serial buffer
    char c = gpsSerial.read();

    // We want to record two NMEA sentences. So start by filling nmea1 buffer...
    if (fill == 1) {
      if (c == '\n') {
        fill = 2;
      }
    // Then fill the nmea2 buffer.
    } else if (fill == 2) {
      if (c == '\n') {
        fill = 1;
        // Once we've got both sentences, set our write flag to true and exit the loop
        dataEnd = true;
        break;
      }
    }
  }
  
  if (dataEnd == true) {
    dataEnd = false;

    // Re-attach the interrupts we removed earlier
    attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
    attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
  }
}

void getInputTime() {
  milli = millis();
  dt = milli - milliLast;
  if(dt > 250) {
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

void filterStep(int controlVector, int measurementVector) {
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
}

