#include "Timer.h"


TimerSW::TimerSW()
{
  Stop();
  SetUnit(millisecond);
  timeStart = 0;
  timeStop = 0;
  running = false;
}
TimerSW::TimerSW(TimeUnit unit_)
{
  Stop();
  SetUnit(unit_);
  Reset();
}
TimerSW::~TimerSW(){}
void TimerSW::Start()
{
  timeStart = CalculateCurTime();
  running = true;
}
void TimerSW::Start(TimeUnit unit_)
{
  SetUnit(unit_);
  Start();
}
void TimerSW::Stop()
{
  if (running)
  {
    timeStop = CalculateCurTime();
    
    timeDifference = CalculateTimeElapsed(timeStart, timeStop);
      
    running = false;
  }
}
void TimerSW::SetUnit(TimeUnit unit_)
{
  if (!running)
  {
    unit = unit_;
    switch (unit)
    {
      case second:
        maxTime = 4294967;
        break;
      case millisecond:
        maxTime = 4294967295;
        break;
      case microsecond:
        maxTime = 4294967295;
        break;
    }
  }
}
void TimerSW::Reset()
{
  timeStart = 0;
  timeStop = 0;
  timeDifference = 0;
  running = false;
}
void TimerSW::Reset(TimeUnit unit_)
{
  SetUnit(unit_);
  Reset();
}
unsigned long TimerSW::GetCurTimeElapsed()
{
  unsigned long timeCur = 0;
  if (running)
    timeCur = CalculateCurTime();
  else
    timeCur = timeStop;
  unsigned long timeDiff = CalculateTimeElapsed(timeStart, timeCur);
  return timeDiff;
}
unsigned long TimerSW::GetTimeElapsed()
{
  return timeDifference;
}
bool TimerSW::GetRunning()
{
  return running;
}
TimeUnit TimerSW::GetUnit()
{
  return unit;  
}

unsigned long TimerSW::CalculateCurTime()
{
  unsigned long time = 0;
  switch (unit)
  {
    case 0:
    {
      time = millis()/1000;
    }
    break;
    case 1:
    {
      time = millis();  
    }
    break;
    case 2:
    {
      time = micros();
    }
    break;
  }
  return time;
}
unsigned long TimerSW::CalculateTimeElapsed(unsigned long t1, unsigned long t2)
{
  unsigned long td = (unsigned long)(t2 - t1);
      
  return td;
}



TimerTarget::TimerTarget(bool initialVal_)
:
timer(millisecond)
{
  Reset(millisecond, 10, initialVal_);
}
TimerTarget::TimerTarget(TimeUnit unit_, unsigned long target_, bool initialVal_)
:
timer(unit_)
{
  Reset(unit_, target_, initialVal_);
}
TimerTarget::~TimerTarget(){}
bool TimerTarget::Check()
{
  unsigned long time = timer.GetCurTimeElapsed();
  if (timer.GetRunning() && time>=timeT)
  {
    timer.Stop();
    state = true;
  }
  return state;
} 
unsigned long TimerTarget::GetTimeRemaining()
{
  if (!timer.GetRunning())
    return 0;

  unsigned long time = timer.GetCurTimeElapsed();
  
  if (time>=timeT)
    return 0;

  return timeT-time;
}

void TimerTarget::Start()
{
  Reset();
  state = false;
  running = true;
  timer.Start();
}
void TimerTarget::Start(unsigned long target_)
{
  timeT = target_;
  Start();
}
void TimerTarget::Reset(TimeUnit unit_, unsigned long target_, bool initialVal_)
{
  timer.Reset(unit_);
  timeT = target_;
  initialVal = initialVal_;
  Reset();
}
void TimerTarget::Reset()
{
  timer.Stop();
  running = false;
  state = initialVal;  
}
bool TimerTarget::GetState()
{
  return state; 
}
bool TimerTarget::GetRunning()
{
  return running;  
}
unsigned long TimerTarget::GetTarget()
{
  return timeT;  
}
