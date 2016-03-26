#include "LCDFController.h"


template <typename dimType>
Coord<dimType> ConvertCoord(dimType x, dimType y)
{
  Coord<dimType> coord;
  coord.x = x;
  coord.y = y;
  return coord;
}
  
LCDFController::LCDFController()                            // default initialisor
:
LCD(DEFAULT_RS, DEFAULT_RW, DEFAULT_ENABLE, DEFAULT_D4, DEFAULT_D5, DEFAULT_D6, DEFAULT_D7),                    // default value
timerRefresh(DEFAULT_UNIT, DEFAULT_TIME)                  // default value
{
  active = false;
  Initialise(DEFAULT_WIDTH, DEFAULT_HEIGHT);                        // default value
}

LCDFController::LCDFController(byte pin_rs,byte pin_rw, byte pin_enable,byte pin_d4, byte pin_d5, byte pin_d6, byte pin_d7, byte width_, byte height_, TimeUnit unit_, unsigned int timeT_)
:
LCD(pin_rs, pin_rw, pin_enable, pin_d4, pin_d5, pin_d6, pin_d7),
timerRefresh(unit_, timeT_)
{
  active = false;
  Initialise(width_, height_, unit_, timeT_);
}

LCDFController::LCDFController(byte width_, byte height_, TimeUnit unit_, unsigned int timeT_)
:
LCD(DEFAULT_RS, DEFAULT_RW, DEFAULT_ENABLE, DEFAULT_D4, DEFAULT_D5, DEFAULT_D6, DEFAULT_D7),                    // default value
timerRefresh(unit_, timeT_)
{
  active = false;
  Initialise(width_, height_, unit_, timeT_);
}

LCDFController::~LCDFController()
{
  Delete();
}

void LCDFController::Reset(byte width_, byte height_, TimeUnit unit_, unsigned int timeT_)
{
  Delete();
  Initialise(width_, height_, unit_, timeT_);
}

void LCDFController::Initialise(byte width_, byte height_, TimeUnit unit_, unsigned int timeT_)
{
  dimension = ConvertCoord<byte>(width_, height_);
  timerRefresh.Reset(unit_, timeT_);
  
  screenBuffer = new char*[dimension.y];                // allocate memory for screenBuffer
	updatedBuffer = new bool*[dimension.y];
  for (byte h=0; h<dimension.y; h++)            // cycle through rows
  {
    screenBuffer[h] = new char[dimension.x];
		updatedBuffer[h] = new bool[dimension.x];
	
		for (byte w=0; w<dimension.x; w++)
		{
			screenBuffer[h][w] = ' ';
			updatedBuffer[h][w] = true;
		}
  }
  
  timerRefresh.Start();
  LCD.begin(dimension.x, dimension.y);
  updated = true;
	refreshed = false;
  active = true;
}
void LCDFController::Initialise(byte width_, byte height_)
{
  Initialise(width_, height_, DEFAULT_UNIT, DEFAULT_TIME);
}
void LCDFController::Delete()
{
  if (active)
  {
    dimension = ConvertCoord<byte>(0,0);
    
    for (byte h=0; h<dimension.y; h++)        // cycle through rows
    {
      delete [] screenBuffer[h];              // delete rows
			delete [] updatedBuffer[h];
    }
    delete [] screenBuffer;                   // delete array of rows
		delete [] updatedBuffer;
    
    updated = false;
    active = false;
  }
}

void LCDFController::Update() 				         // updates the characters that have been updated
{
	if (!updated)
		return;
  if (timerRefresh.Check())                    // checks whether the LCD should be reset
  {
    //LCD.clear();                               // clears LCD
    
    for (byte h=0; h<dimension.y; h++)         // cycles through rows of characters
    {
			                                         // cycle through the row
			for (byte w=0; w<dimension.x; w++)
			{
				if (updatedBuffer[h][w])
				{
					LCD.setCursor(w,h);                  // sets cursor to beginning of each row
					LCD.print(screenBuffer[h][w]);       // prints a row of characters
					updatedBuffer[h][w] = false;				 // do not need to update this char again
				}
			}
    }
    
		refreshed = true;
    updated = false;                           // resets the updated variable
    timerRefresh.Reset();                      // restarts timer
    timerRefresh.Start();                      // restarts timer
  }
}

void LCDFController::ForceRefresh()
{
	updated = true;
	for (byte h=0; h<dimension.y; h++)
		for (byte w=0; w<dimension.x; w++)
			updatedBuffer[h][w] = true;
	LCD.clear();
	Update();
}


void LCDFController::SetText(byte x, byte y, char text)
{ SetText(ConvertCoord<byte>(x,y), text); }

// "Master" function
void LCDFController::SetText(Coord<byte> coord, char text)                  
{ 
  ChangeChar(coord, text); 
}

void LCDFController::SetText(byte x, byte y, char* text)
{ SetText(ConvertCoord<byte>(x,y),text); }

void LCDFController::SetText(Coord<byte> coord, char* text)
{
  if (CheckCoord(coord))
  {
    byte lim = dimension.x-coord.x;                        // maximum value of iterations in for loop
    for (byte i=0; i<lim; i++)
    {
      if (text[i] == '\0')                                        // checks for terminator character
        return;
      
      SetText(coord.x+i, coord.y, text[i]);
    }
  }
}

void LCDFController::SetText(byte x, byte y, char* text, byte len)
{ SetText(ConvertCoord<byte>(x,y),text, len); }
  
void LCDFController::SetText(Coord<byte> coord, char* text, byte len)
{
  if (CheckCoord(coord))
  {
    byte lim = min( dimension.x-coord.x , len );
    for (byte i=0; i<lim; i++)
    {      
      SetText(coord.x+i, coord.y, text[i]);
    }
  }
}

void LCDFController::SetText(byte x, byte y, String text)
{ SetText(ConvertCoord<byte>(x,y),text); }
  
void LCDFController::SetText(Coord<byte> coord, String text)
{
  char* text_ = (char*)(text.c_str());                           // gets character array (null-terminated)
  SetText(coord, text_);                                         // runs SetText function with char array
}



void LCDFController::Clear(bool clearLCD)                   // clears buffer (actually fills in with spaces ' ')
{
  if (clearLCD)
    LCD.clear();
  for (byte h=0; h<dimension.y; h++)                  // cycle through rows
  {
    for (byte w=0; w<dimension.x; w++)                // cycle through positions in row
    {
      SetText(w,h,' ');
    }
  }
}



bool LCDFController::GetActive()
{
  return active;
}
bool LCDFController::GetUpdated()
{
  return updated;
}
bool LCDFController::GetRefreshed()
{
  return refreshed;
}
byte LCDFController::GetWidth()
{
  return dimension.x;
}
byte LCDFController::GetHeight()
{
  return dimension.y;
}
Coord<byte> LCDFController::GetDimensions()
{
  return dimension;
}


void LCDFController::ChangeChar(Coord<byte> coord, char text)      // limit determines whether the coordinates must be checked
{
  if (active)
  {
    if (CheckCoord(coord))                  // checks coordinate
    {
			refreshed = false;
			if (text != screenBuffer[coord.y][coord.x])
			{
				updated = true;
				updatedBuffer[coord.y][coord.x] = true;				
			}
      screenBuffer[coord.y][coord.x] = text;
    }
  }
}
bool LCDFController::CheckWidth(byte input)
{
  return (dimension.x > input);
}
bool LCDFController::CheckHeight(byte input)
{
  return (dimension.y > input);
}
bool LCDFController::CheckCoord(Coord<byte> input)
{
  return (CheckWidth(input.x) && CheckHeight(input.y));
}
