#include <SD.h>
#include <SPI.h>

#define ledPin 13
#define chipSelect 10

volatile uint32_t milli = millis();
volatile uint32_t milliLast = millis();
volatile uint32_t dt = 0;
volatile uint32_t ppsMilli = millis();
volatile uint32_t ppsMilliLast = millis();
volatile uint32_t ppsDt = 0;

int writeNow = 0;
int ppsWriteNow = 0;

File logfile;

// blink out an error code
void error(uint8_t errno) {
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
  strcpy(filename, "PPSSER00.TXT");
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
  
  attachInterrupt(digitalPinToInterrupt(3), getInputTime, RISING);
  attachInterrupt(digitalPinToInterrupt(2), getPPSTime, RISING);
}


void loop() {

  if (writeNow && ppsWriteNow) {
    writeData();
    writeNow = 0;
    ppsWriteNow = 0;
  }

}

void getInputTime() {
  noInterrupts();
  milli = millis();
  dt = milli - milliLast;
  if(dt > 200) {
    milliLast = milli;
    writeNow = 1;
  }
  interrupts();
}

void getPPSTime() {
  noInterrupts();
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
  interrupts();
}


void writeData() {
  logfile.println(String(milliLast) + "," + String(ppsMilliLast));
  logfile.flush();
}

