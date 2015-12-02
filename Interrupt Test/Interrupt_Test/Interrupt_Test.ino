#include <SD.h>
#include <SPI.h>

#define ledPin 13
#define chipSelect 10

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;

int writeNow = 0;

File logfile;

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
  pinMode(3, INPUT);
  // Chip select for SD
  pinMode(10, OUTPUT);

    // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {      // if you're using an UNO, you can use this line instead
    error(2);
  }
  char filename[15];
  strcpy(filename, "GPSLOG00.TXT");
  for (uint8_t i = 0; i < 100; i++) {
    filename[6] = '0' + i/10;
    filename[7] = '0' + i%10;
    // create if does not exist, do not open existing, write, sync after write
    if (! SD.exists(filename)) {
      break;
    }
  }

  logfile = SD.open(filename, FILE_WRITE);
  if( ! logfile ) {
    error(3);
  }
  
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, CHANGE);
}


void loop() {

  if (writeNow) {
    writeData();
    writeNow = 0;
  }

}

void getInputTime() {
  milli = millis();
  dt = milli - milliLast;
  if(dt > 200) {
    milliLast = milli;
    writeNow = 1;
  }
}

void writeData() {
  logfile.println(String(dt));
  logfile.flush();
}

