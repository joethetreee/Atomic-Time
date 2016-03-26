#include "Button.h"

Button::Button(byte buttonPin)
:
timer(microsecond,5)
{
  pin = buttonPin;
  UpdateState();
}
Button::~Button(){}
void Button::UpdateState()
{    
  bool tempState = Debounce();
  
  if (timer.Check())
  {
    state = tempState;
    timer.Reset();
  }
}
bool Button::GetState()
{
  return state;
}
bool Button::Debounce()
{
  if (!timer.GetRunning())                      // checks whether timer has been started
  {
    if (state != digitalRead(pin))     // there is a change; set up variables which are used to verify change
    {
      timer.Start();
    }
  }
    
  return digitalRead(pin);
}


ButtonM::ButtonM(byte buttonPin, int stateNo_)        // multi-toggle button
:
button(buttonPin)
{
  state = LOW;
  stateNo = stateNo_;
}
ButtonM::~ButtonM(){}
void ButtonM::UpdateState()
{
  bool prevBState = button.GetState();          // gets previous state of push button
  button.UpdateState();
  bool curBState = button.GetState();            // gets updated state of push button
  
  if (curBState == LOW && prevBState==HIGH)
    IncrementState();
}
void ButtonM::IncrementState()
{
  SetState(state+1);
}
void ButtonM::SetState(unsigned int state_)
{
  ChangeState(state_);
}
void ButtonM::ChangeState(unsigned int state_)
{
    state = state_%stateNo;
}
int ButtonM::GetState()
{
  return state;
}




ButtonMH::ButtonMH(byte buttonPin, int stateNo_, TimeUnit unit_, unsigned long timeT1)        // multi-toggle button which cycles state while held
:
button(buttonPin),
timer(unit_,timeT1)
{
  Create(stateNo_, timeT1);
}
ButtonMH::ButtonMH(byte buttonPin, int stateNo_)        // multi-toggle button
:
button(buttonPin),
timer(microsecond,500)
{
  Create(stateNo_, 500);
}
void ButtonMH::Create(int stateNo_, unsigned long timeT)
{
  state = LOW;
  stateNo = stateNo_;
  holdStage = 0;
  target = timeT;
}
ButtonMH::~ButtonMH(){}
void ButtonMH::UpdateState()
{
  bool prevBState = button.GetState();          // gets previous state of push button
  button.UpdateState();                            // updates state of push button
  bool curBState = button.GetState();            // gets updated state of push button
  
  if (curBState == HIGH)
  {
    // activate button for the first time
    if (holdStage==0)
    {
      if (prevBState==LOW)                        // button has just been pressed
      {
        holdStage = 1;
        timer.Start(target);
      }
    }
    
    // check for hold activations
    else if (CheckHold())
      ChangeState(true);
  }
  else                                          // button is not held
  {
    if (holdStage == 1)
      ChangeState(false);
    else if (holdStage == 2)
      ChangeState(true);
    holdStage = 0;
  }
}
void ButtonMH::ChangeState(bool hold)
{
  if (hold)
  {
    state += stateNo;
    state %= (stateNo*2);  
  }
  else
  {
    state += 1;
    state %= stateNo;
  }
}
int ButtonMH::GetState()
{
  return state;
}
bool ButtonMH::CheckHold()
{
  if (timer.Check() && holdStage!=0)
  {
    holdStage = 2;
    timer.Reset();
    return true; 
  }
  return false; 
}



ButtonMC::ButtonMC(byte buttonPin, int stateNo_, TimeUnit unit_, unsigned long timeT1, unsigned long timeT2)        // multi-toggle button which cycles state while held
:
button(buttonPin),
timer(unit_,timeT1)
{
  Create(stateNo_, timeT1, timeT2);
}
ButtonMC::ButtonMC(byte buttonPin, int stateNo_)        // multi-toggle button
:
button(buttonPin),
timer(microsecond,500)
{
  Create(stateNo_, 500, 100);
}
void ButtonMC::Create(int stateNo_, unsigned long timeT1, unsigned long timeT2)
{
  state = LOW;
  stateNo = stateNo_;
  holdStage = 0;
  target1 = timeT1;
  target2 = timeT2;
}
ButtonMC::~ButtonMC(){}
void ButtonMC::UpdateState()
{
  bool prevBState = button.GetState();          // gets previous state of push button
  button.UpdateState();                            // updates state of push button
  bool curBState = button.GetState();            // gets updated state of push button
  
  if (curBState == HIGH)
  {
    // activate button for the first time
    if (holdStage==0)
    {
      if (prevBState==LOW)
      {
        holdStage = 1;
        ChangeState();
      }
    }
    
    // check for hold activations
    else if (CheckHold())
      ChangeState();
  }
  else
    holdStage = 0;
}
void ButtonMC::ChangeState()
{
    state += 1;
    state %= stateNo;
    
    if (holdStage==1)
      timer.Start(target1);
    else
      timer.Start(target2);
}
int ButtonMC::GetState()
{
  return state;
}
bool ButtonMC::CheckHold()
{
  if (timer.Check() && holdStage!=0)
  {
    holdStage = 2;
    return true; 
  }
  return false; 
}

ButtonT::ButtonT(byte buttonPin, TimeUnit tUnit)
:
button(buttonPin),
timer(tUnit)
{
  SetTimeUnit(tUnit);
}
ButtonT::~ButtonT()
{}
int ButtonT::UpdateState()
{
  button.UpdateState();
  if (button.GetState() && !timer.GetRunning())  // if button has just been pressed
  {
    timer.Reset();
    timer.Start();
  }
  if (!button.GetState() && timer.GetRunning())  // if button has just been released
    timer.Stop();
  return GetHoldTime();
}
void ButtonT::Reset()
{
  timer.Reset();
}

int ButtonT::GetHoldTime()
{
  return timer.GetTimeElapsed();
}

TimeUnit ButtonT::GetTimeUnit()
{
  return timer.GetUnit();
}

void ButtonT::SetTimeUnit(TimeUnit tUnit)
{
  timer.SetUnit(tUnit);
}
