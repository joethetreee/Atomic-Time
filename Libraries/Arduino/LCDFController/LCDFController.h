
#ifndef LCDFController_H
#define LCDFController_H

#include "Arduino.h"
#include <LiquidCrystalFast.h>
#include <Timer.h>


// LCD
#define DEFAULT_UNIT     millisecond  // default unit for refresh timer
#define DEFAULT_TIME     200          // default number of time units for refresh
#define DEFAULT_RS       47           // default RS pin for LCD
#define DEFAULT_RW       48           // default RW pin for LCD
#define DEFAULT_ENABLE   46           // default enable pin for LCD
#define DEFAULT_D4       45           // defualt D4 pin
#define DEFAULT_D5       44           // default D5 pin
#define DEFAULT_D6       43           // default D6 pin
#define DEFAULT_D7       42           // default D7 pin
#define DEFAULT_WIDTH    8            // default width of LCD display
#define DEFAULT_HEIGHT   2            // default height of LCD display


template <typename dimType>
struct Coord
{
  dimType x;
  dimType y;
};

template <typename dimType>
Coord<dimType> ConvertCoord(dimType x, dimType y);

class LCDFController                            // stores LCD object, a character buffer and a timer for refresh rate
{
public:
  LCDFController();
  LCDFController(byte pin_rs,byte pin_rw,byte pin_enable, byte pin_d4, byte pin_d5, byte pin_d6, byte pin_d7, byte width, byte height, TimeUnit unit, unsigned int timeT_);
  LCDFController(byte width_, byte height_, TimeUnit unit, unsigned int timeT_);
  ~LCDFController();
  
  void Reset(byte width_, byte height_, TimeUnit unit_, unsigned int timeT_);
  
  void Update();                                                    // draws/clears screen based on timer
  
  void SetText(byte x, byte y, char text);
  void SetText(Coord<byte> coord, char text);
  void SetText(byte x, byte y, char* text);
  void SetText(Coord<byte> coord, char* text);
  void SetText(byte x, byte y, char* text, byte len);
  void SetText(Coord<byte> coord, char* text, byte len);
  void SetText(byte x, byte y, String text);
  void SetText(Coord<byte> coord, String text);
  void Clear(bool clearLCD);                                     // clears buffer (actually fills in with spaces ' '). clearLCD is whether to physically clear LCD.
  void ForceRefresh();											// refreshes the screen (useful if characters are bugged and not changed)
  
  bool GetActive();
  bool GetUpdated();                                            // returns whether the screenBuffer has been updated within current refresh time
  bool GetRefreshed();                                            // returns whether the screenBuffer has been attemped-updated within current refresh time
  byte GetWidth();
  byte GetHeight();
  Coord<byte> GetDimensions();
    
private:
  void Initialise(byte width_, byte height_, TimeUnit unit_, unsigned int timeT_);
  void Initialise(byte width_, byte height_);
  void Delete();
  
  // IMPORTANT: ChangeChar is the function which actually sets text.
  void ChangeChar(Coord<byte> coord, char text);      // limit determines whether the coordinates must be checked
  bool CheckWidth(byte input);
  bool CheckHeight(byte input);
  bool CheckCoord(Coord<byte> input);

  LiquidCrystalFast LCD;
  TimerTarget timerRefresh;
  Coord<byte> dimension;
  
  char** screenBuffer;                  // char[height][width]
  bool active;                          // keeps track of whether delete [] should be called for screenBuffer
  bool updated;                         // keeps track of whether the buffer has been updated since the last refresh (can be used to cut down on work - doesn't render unnecessary frames)
	bool refreshed;												// whether the lcd has just been refreshed, and no attempt has been made to write to buffer
  bool** updatedBuffer;									// keeps track of whether each character has been updated
};

//class LCDFController                                    // stores a list of LCD instances and IDs



#endif
