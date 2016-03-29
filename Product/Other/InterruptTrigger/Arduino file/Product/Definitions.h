#include "Arduino.h"
#include <Timer.h>

// Definitions
extern bool serialActive;

// pin Definitions
// __ __ __ __ __ __ __

byte pinLedPps = 21;
byte pinLedFix = 22;

byte pinButRes = 19;
byte pinButMod = 20;

  // LCD
byte pinLCDRS = 2;
byte pinLCDRW = 8;
byte pinLCDEn = 3;
byte pinLCDD4 = 4;
byte pinLCDD5 = 5;
byte pinLCDD6 = 6;
byte pinLCDD7 = 7;

TimeUnit lcdTimeUnit = millisecond;
unsigned int lcdTimeRefresh = 200;

  // GPS
byte pinGPSSerIn = 9;
byte pinGPSSerOut = 10;
byte pinGPSPps = 17;

byte pinPpsOut = 16;          // pin for our pps out
int pulseLen = 100;           // length of PPS pulse out in milliseconds
bool fix = false;             // whether there is a fix or not
byte satNum = 0;              // number of connected satellites
byte satNumPrev = 0;          // previous number of connected satellites
byte pulseEstArmed = 0;       // which estimate triggers pulse

  // SD
byte pinSDCS = 14;
extern bool sdActive;
  
  // kalman data

// PPS Distribution Offset Average from kalman_ard.py on GPSMIL37ChckdCor.txt dataset; do not have data for 0,1,2 satellites -- just filled in as appropriate
#define SATDATA_NUM 12        // number of satellite connections with data
int satOffsets[12] = {200, 205, 215, 224, 233, 245, 262, 281, 294, 304, 320, 303};
int satUncerts[12] = {50 , 40 , 30 , 12 , 14 , 18 , 21 , 22 , 23 , 22 , 18 , 10 };
float clockDriftSec = 0.0005; // estimate of clock drift per second

// Software reset definitions
// __ __ __ __ __ __ __

#define RESTART_ADDR       0xE000ED0C
#define READ_RESTART()     (*(volatile uint32_t *)RESTART_ADDR)
#define WRITE_RESTART(val) ((*(volatile uint32_t *)RESTART_ADDR) = (val))
