#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);

void setup() {
    
  Serial.begin(9600);
  GPS.begin(9600);
  delay(1000);
}

uint32_t time1 = millis();

void loop() {
  // in case you are not using the interrupt above, you'll
  // need to 'hand query' the GPS, not suggested :(
  if (GPS.available()) {
    if (millis() - time1 > 500) {
      Serial.println(millis() - time1);
      time1 = millis();
    }
    char c = GPS.read();
  }
}
