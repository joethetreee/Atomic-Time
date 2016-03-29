#ifndef H_BUTTON
#define H_BUTTON

/*
Button library by Duncan Robinson
Use how you like
*/

#include <Timer.h>
#include "Arduino.h"

class Button            // ordinary push button
{
public:
  Button(byte buttonPin);
  ~Button();
  void UpdateState();
  bool GetState();
private:  
  bool Debounce();
  byte pin;
  bool state;
  TimerTarget timer;
};

class ButtonM       // multi-toggle button
{
public:
  ButtonM(byte buttonPin, int stateNo_);
  ~ButtonM();
  void UpdateState();
  void IncrementState();
  void SetState(unsigned int state_);
  int GetState();
private:
  void ChangeState(unsigned int state_);
  
  Button button;     // stores state of push button
  
  int state;        // stores toggle state
  int stateNo;      // stores number of states
};

class ButtonMH      // multi-toggle button which can access a different state from each state by being held for a period of time
// e.g. a button with states 1-3 have "shadow" states 4-6. 1 can access 4, 2 can access 5, 3 can access 6.
{
public:
  ButtonMH(byte buttonPin, int stateNo_, TimeUnit unit_, unsigned long timeT);
  ButtonMH(byte buttonPin, int stateNo_);
  ~ButtonMH();
  void UpdateState();
  int GetState();
private:
  void Create(int stateNo_, unsigned long timeT);
  void ChangeState(bool hold);            // hold is whether the change is a result of being held down or pressed
  bool CheckHold();
  
  Button button;     // stores state of push button
  
  int state;        // stores toggle state
  int stateNo;      // stores number of states (doesn't include the "double" states
  
  
  // variables for dealing with cycling through states when button is held
  TimerTarget timer;            // computes timings of subsequent activations
  unsigned long target;    // time required to go to hold state
  unsigned int holdStage;  // stores stage of hold: 0 is unheld, 1 is between 1st and 2nd activation, 2 is after 2nd activation. 1 and 2 are "held" states.
  bool holdState;    // stores activation
};

class ButtonMC      // multi-toggle button which cycles through states while held
{
public:
  ButtonMC(byte buttonPin, int stateNo_, TimeUnit unit_, unsigned long timeT1, unsigned long timeT2);
  ButtonMC(byte buttonPin, int stateNo_);
  ~ButtonMC();
  void UpdateState();
  int GetState();
private:
  void Create(int stateNo_, unsigned long timeT1, unsigned long timeT2);
  void ChangeState();
  bool CheckHold();
  
  Button button;     // stores state of push button
  
  int state;        // stores toggle state
  int stateNo;      // stores number of states
  
  
  // variables for dealing with cycling through states when button is held
  TimerTarget timer;            // computes timings of subsequent activations
  unsigned long target1;    // time between first and second activations
  unsigned long target2;    // time between subsequent activations
  unsigned int holdStage;  // stores stage of hold: 0 is unheld, 1 is between 1st and 2nd activation, 2 is after 2nd activation. 1 and 2 are "held" states.
  bool holdState;    // stores activation
};

class ButtonT    // timer button -- when button is pressed and released, hold time is returned
{
public:
  ButtonT(byte buttonPin, TimeUnit tUnit);
  ~ButtonT();
  int UpdateState();
  int GetHoldTime();
  void Reset();
  TimeUnit GetTimeUnit();
  void SetTimeUnit(TimeUnit tUnit);
private:
  Button button;
  TimerSW timer;
};

#endif
