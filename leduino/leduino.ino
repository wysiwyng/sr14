/*
#    Copyright (C) 2105  wysiwyng
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

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
  byte in1 = digitalRead(2);
  byte in2 = digitalRead(3);
  byte in3 = digitalRead(4);
  
  if(in1 == LOW && in2 == LOW)
    in = 0;
  else if (in1 == HIGH && in2 == LOW)
    in = 1;
  else if (in1 == LOW && in2 == HIGH)
    in = 2;
  else if (in1 == HIGH && in2 == HIGH)
    in = 3;
  
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
  for (int i = 27; i < 33; i++)
    strip.setPixelColor(i, strip.Color(127, 127, 127));
    
  if (in3 == HIGH)
  {
    val = (exp(sin(millis()/100.0*PI)) - 0.36787944)*54.0;
    uint32_t color2 = strip.Color(val, val / 2, 0);
    strip.setPixelColor(2, color2);
    strip.setPixelColor(3, color2);
    strip.setPixelColor(11, color2);
    strip.setPixelColor(12, color2);
    strip.setPixelColor(20, color2);
    strip.setPixelColor(21, color2);    
  }
  strip.show();
}
