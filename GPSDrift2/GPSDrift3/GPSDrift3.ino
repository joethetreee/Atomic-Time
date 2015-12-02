#include <SPI.h>
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>
#include <SD.h>

SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);

#define ledPin 13
#define chipSelect 10

char nmea1[80];
char nmea2[80];
char charGPS;
int count1 = 0;
int count2 = 0;
int current = 1;

int write1 = 0;
int write2 = 0;

File logfile;
uint32_t timeLast = millis();
uint32_t diff = 0;

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

  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  // Set up a char buffer to read serial data
  // NMEA specification states each message can be up to 80 bytes long including CR/LF
  for(int i = 0; i < 80; i++) {
    nmea1[i] = ' ';
    nmea2[i] = ' ';
  }

  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);

  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {      // if you're using an UNO, you can use this line instead
    Serial.println("Card init. failed!");
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
    Serial.print("Couldnt create "); 
    Serial.println(filename);
    error(3);
  }
  Serial.print("Writing to "); 
  Serial.println(filename);

  // connect to the GPS at the desired rate
  GPS.begin(9600);

  // RMC and GGA
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);

  // 1Hz update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);

  // Turn off updates on antenna status, if the firmware permits it
  GPS.sendCommand(PGCMD_NOANTENNA);

  Serial.println("GPSDrift v3");
  Serial.println("Ready!");
}

void loop() {
  if(mySerial.overflow()) {
    Serial.println("SoftwareSerial overflow!"); 
  }

  while(mySerial.available()) {
    charGPS = GPS.read();
    
    if(charGPS) {
      if(millis() - timeLast > 750) {
        diff = millis() - timeLast;
        timeLast = millis();
      }
  
      // We don't want the CR at the end of the char as it makes the log files messy
      // This actually puts a newline at the start of the message as it wraps from the previous message
      if(charGPS != 13) {
        if(current == 1) {
          nmea1[count1] = charGPS;
          count1++;
        } else if(current == 2) {
          nmea2[count2] = charGPS;
          count2++;
        }
      }
    
      if(charGPS == 13) {
        if(current == 1) {
          nmea1[count1] = '\0';
          write1 = 1;
          current = 2;
          Serial.print(nmea1);
        } else if(current == 2) {
          nmea2[count2] = '\0';
          write2 = 1;
          current = 1;
          Serial.print(nmea2);
        }
      }
    }
  }

  if(write1 == 1) {
    // Write to SD card
    uint8_t stringsize = strlen(nmea1);
    if (stringsize != logfile.write((uint8_t *)nmea1, stringsize)) {    //write the string to the SD file
      Serial.println("Write error");
    } else {
      logfile.print("," + String(diff));
      logfile.flush();
      Serial.print("Logged");
    }
    
    // Clear buffer for next sentence
    for(int i = 0; i < 80; i++) {
      nmea1[i] = ' ';
    }
    
    // Reset the character count
    count1 = 0;
    write1 = 0;
  } else if(write2 == 1) {
    // Write to SD card
    uint8_t stringsize = strlen(nmea2);
    if (stringsize != logfile.write((uint8_t *)nmea2, stringsize)) {    //write the string to the SD file
      Serial.println("Write error");
    } else {
      logfile.print("," + String(diff));
      logfile.flush();
      Serial.print("Logged");
    }
    
    // Clear buffer for next sentence
    for(int i = 0; i < 80; i++) {
      nmea2[i] = ' ';
    }
    
    // Reset the character count
    count2 = 0;
    write2 = 0;
  }
}
