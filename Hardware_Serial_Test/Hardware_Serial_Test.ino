volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();

void setup() {
  Serial.begin(9600);
  pinMode(3, INPUT);
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, CHANGE);
}


void loop() {

}

void getInputTime() {
  milli = millis();
  if(milli - milliLast > 200) {
    Serial.println(milli - milliLast);
    milliLast = milli;
  }
}

