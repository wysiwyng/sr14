#include "LPD8806.h"
#include "SPI.h"

#define standbySpeed 3000.0
#define standbyColor strip.Color(val, val, val / 1.3)

#define attackSpeed 300.0
#define attackColor strip.Color(val, 0, 0)

#define idleSpeed 2000.0
#define idleColor strip.Color(val / 3, val, 0) // set a timer of length 100000 microseconds (or 0.1 sec - or 10Hz => the led will blink 5 times, 5 cycles of on-and-off, per second)

#define scoreSpeed 50.0
#define scoreColor i % 4 == 0 ? strip.Color(val, val, val) : strip.Color(0, val / 2, val)

LPD8806 strip = LPD8806(36);

volatile int val = 0.0;
volatile byte mode = 0; //0: standby, 1: idle, 2: attack, 3: score, 4: victory
float speed = 0.0;
volatile uint32_t color = 0;

void standby()
{
  mode = 0;
  speed = standbySpeed;
}

void idle()
{
  mode = 1;
  speed = idleSpeed;
}

void attack()
{
  mode = 2;
  speed = attackSpeed;
}

void score()
{
  mode = 3;
  speed = scoreSpeed;
}

void setup()
{
  pinMode(2, INPUT);
  pinMode(3, INPUT);
  pinMode(4, INPUT);
  
  strip.begin();
  
  // Update the strip, to start they are all 'off'
  strip.show();
  
  standby();  
}
byte in = 0;
void loop()
{
  if(digitalRead(2) == HIGH) in = 1;
  else if(digitalRead(3) == HIGH) in = 2;
  else if(digitalRead(4) == HIGH) in = 3;
  else in = 0;
  switch(in)
  {
    case 0:
      standby();
      break;
    case 1:
      idle();
      break;
    case 2:
      attack();
      break;
    case 3:
      score();
      break;
  }
 
  val = (exp(sin(millis()/speed*PI)) - 0.36787944)*54.0;
  for (int i=0; i < strip.numPixels(); i += 2) 
  {
    
    switch(mode)
    {
      case 0:
        color = standbyColor;
        break;
      case 1:
        color = idleColor;
        break;

      case 2:
        color = attackColor;
        break;
      case 3:
        color = scoreColor;
        break;
    }
    
    strip.setPixelColor(i, color);
    strip.setPixelColor(i + 1, color);
  }
  strip.show();
}
