/* reading from serial
 *  1: measure and return
 */

bool firstMeasure;
int offset;

void SerialClear()
{
  while (Serial.available()>0)
    byte b = Serial.read();
}

void setup()
{
  firstMeasure = true;
  Serial.begin(9600);
  SerialClear();
}

void loop()
{
  signed char msg = '0'-1;
  while (Serial.available()>0)
  {
    msg = Serial.read();
  }
    
  msg -= '0';

  if (msg == -1)
  {
    return;
  }

//  Serial.println();
//  Serial.println(msg);
    
  if (msg == 1)
  {
    long t = millis();
    if (firstMeasure)
    {
      offset = t;
      firstMeasure = false;
    }
    Serial.println(t-offset);
  }
  else
  {
    Serial.println(-1);
  }
}
