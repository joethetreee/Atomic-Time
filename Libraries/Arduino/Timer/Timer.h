/*
Timer library by Duncan Robinson
Use however you like
*/


#ifndef TIMER_H
#define TIMER_H

#include "Arduino.h"

enum TimeUnit
{
  second,
  millisecond,
  microsecond,
};


class TimerSW                            // stop watch timer
{
public:
  TimerSW();
  TimerSW(TimeUnit unit_);
  ~TimerSW();
  void Start();
  void Start(TimeUnit unit_);
  void Stop();
  void SetUnit(TimeUnit unit_); 
  void Reset(); 
  void Reset(TimeUnit unit_);
  unsigned long GetCurTimeElapsed();
  unsigned long GetTimeElapsed();
  bool GetRunning();
  TimeUnit GetUnit();
private:
  unsigned long CalculateCurTime();
  unsigned long CalculateTimeElapsed(unsigned long t1, unsigned long t2);

  TimeUnit unit;        // unit in which time is measured
  unsigned long timeStart;  // time at which timer was started
  unsigned long timeStop;  // time at which timer was stopped
  unsigned long timeDifference;  // difference between timeStart and timeStop
  bool running;      // whether timer is running
  unsigned long maxTime;  // maximum time before timer resets
};


class TimerTarget                      // Activates after target_ time
{
public:
  TimerTarget(bool initialVal__=false);
  TimerTarget(TimeUnit unit_, unsigned long target_, bool initialVal__=false);
  ~TimerTarget();
  bool Check();          // checks whether the timer has reached target_ and returns activation state
unsigned long GetTimeRemaining();
  void Start();
  void Start(unsigned long target_);
  void Reset(TimeUnit unit_, unsigned long target_, bool initialVal__=false);            // deactivates and resets values
  void Reset();                        // deactivates
  bool GetRunning();
  bool GetState();
  unsigned long GetTarget();
private:
  TimerSW timer;          // works out timing
  bool state;        // true if activated. Activated when timer reaches target_
  bool running;          // true if timer has been started and not reset
  bool initialVal;       // value state takes if timer is reset
  unsigned long timeT;	// target_ time
};

#endif
