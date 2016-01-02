int lowVal = 900;
int hiVal = 1100;

void setup()
{
  Serial.begin(9600);
  randomSeed(analogRead(0));
}

void loop()
{
  int valT = random(lowVal,hiVal);
  int tStart = millis();
  int tCur = millis();
  while (tCur-tStart<valT)
    tCur = millis();

  Serial.print(valT);
  Serial.print(",");
  Serial.println(tCur-tStart);
}
