#include "wiring_private.h"
#include "pins_arduino.h"
#include <TimerThree.h>
#include <avr/wdt.h>

//#define debug

#define VERSION 123

#define pi 3.14159265


#define encoder0pinA PIN_D0

#define encoder1pinA PIN_D1


#define dir0A PIN_D6    //PD6
#define dir0A_on (PORTD |= (1 << 6))
#define dir0A_off (PORTD &= ~(1 << 6))

#define dir0B PIN_D4     //PD4
#define dir0B_on (PORTD |= (1 << 4))
#define dir0B_off (PORTD &= ~(1 << 4))

#define dir1A PIN_B4     //PB4
#define dir1A_on (PORTB |= (1 << 4))
#define dir1A_off (PORTB &= ~(1 << 4))

#define dir1B PIN_D7     //PD7
#define dir1B_on (PORTD |= (1 << 7))
#define dir1B_off (PORTD &= ~(1 << 7))

#define pwm0 PIN_B5
#define pwm1 PIN_B6

#define wheelDiameter 11
#define wheelDistance 46
#define cpr 1600

#define cpcm cpr/(wheelDiameter*pi)
#define cmpd (wheelDistance*pi)/360

#define maxFaults 20
#define minSpeed 5

word c0;
word c1;

double dist;

byte overflow;

volatile int duration0;//Encoder0 number of pulses
volatile int duration1;//Encoder1 number of pulses

int setPoint = 0; // 0 would be straight ahead
double p = 10; // needs tuning
int error = 0;
int speed = 0; // set the speed of which the vechicle should move
int output = 0;

volatile int faultCount = 0;

volatile boolean completed = true;
volatile boolean fault = false;
volatile boolean preFault = false;

byte counter = 0;
byte vars[5] = {
  0, 0, 0, 0, 0};

void setup()
{
  MCUSR &= ~(1 << WDRF);
  wdt_disable();

  pinMode(pwm0, OUTPUT);
  pinMode(pwm1, OUTPUT);
  pinMode(dir0A, OUTPUT);
  pinMode(dir0B, OUTPUT);
  pinMode(dir1A, OUTPUT);
  pinMode(dir1B, OUTPUT);

  motorsFloat();

  Serial.begin(115200); //Initialize the serial port
#ifdef debug
  Serial1.begin(115200);
#endif
  attachInterrupt(0, wheelSpeed0, CHANGE);
  attachInterrupt(1, wheelSpeed1, CHANGE);

  Timer3.initialize(20000);
  Timer3.attachInterrupt(timer3_int);
  Timer3.start();
  byte lamps[4] = {
    dir0A, dir0B, dir1A, dir1B      };
  boolean temp = LOW;

  for(int i = 0; i < 4; i++){
    digitalWrite(lamps[i], 1);
    delay(100);
  }
  for(int i = 0; i < 4; i++){
    digitalWrite(lamps[i], 0);
    delay(100);
  }  

#ifdef debug
  Serial1.println("ready");
#endif

  motorsBrake();
}

void loop()
{
  if(Serial.available())
  {
    byte rec = Serial.read();
#ifdef debug
    Serial1.print("in byte: ");
    Serial1.println(rec);
    Serial1.print("count: ");
    Serial1.println(counter);
#endif
    if(counter > 0 || rec == '$') counter++;
    if(counter > 1) vars[counter - 2] = rec;
    if(counter == 0)
    {
      switch(rec)
      {
      case 'v':
        Serial.write(VERSION);
        break;
      }
    }
    if(counter == 6)
    {
      counter = 0;
      byte instruction = vars[0];
      speed = vars[1];
      setPoint = vars[2];
      boolean f = bitRead(instruction,2);
      boolean turn = bitRead(instruction,1);
      boolean brake = bitRead(instruction,0); 
#ifdef debug
      Serial1.println("complete command received");
      Serial1.println(instruction);
      Serial1.println(speed);
      Serial1.println(setPoint);
      Serial1.println(word(vars[3], vars[4]));
#endif

      if(brake)
      {
        motorsBrake();
      }
      else if(speed == 0)
      {
        motorsFloat();
      }
      else 
      {
        if(turn)
        {
          dist = word(vars[3], vars[4]) * cmpd;
          setPoint = 0;
          if(f)
          {
            PORTD |= (1 << 4);
            PORTD &= ~((1 << 6) | (1 << 7));
            PORTB |= (1 << 4);
          }
          else
          {
            PORTD &= ~(1 << 4);
            PORTD |= ((1 << 6) | (1 << 7));
            PORTB &= ~(1 << 4);
          }
        }
        else
        {
          dist = word(vars[3], vars[4]);
          if(f)
          {
            PORTD &= ~(1 << 6);
            PORTD |= ((1 << 4) | (1 << 7));
            PORTB &= ~(1 << 4);
          }
          else if (!f)
          {
            PORTD |= (1 << 6);
            PORTD &= ~((1 << 4) | (1 << 7));
            PORTB |= (1 << 4);
          }
        }
        enableTimers();
      }

      if(dist > 0) completed = false;
      fault = false;
#ifdef debug
      Serial1.println("waiting for completion");
#endif
      while(!completed) ;
#ifdef debug
      Serial1.println("completed");
#endif
      Serial.print('$');
      if(fault) bitClear(instruction, 3);
      Serial.write(instruction);
      Serial.write(vars[1]);
      Serial.write(vars[2]);
      Serial.write(vars[3]);
      Serial.write(vars[4]);
    }
  }
}

void checkRev()
{
  if(dist==0 || speed==0) {
    return;
  }
  noInterrupts();
  if(c0 >= (dist*cpcm) || c1 >= (dist*cpcm))
  {
    motorsBrake();
    resetVars();
    fault = false;
  }
  interrupts();
}

void timer3_int()
{
  if((duration0 < minSpeed || duration1 < minSpeed) && speed > 0)
  {
    if(preFault) faultCount++;
    else 
    {
      preFault = true;
      faultCount = 0;
    }
  }
  else preFault = false;
  
  if(faultCount > maxFaults)
  {
    motorsBrake();
    resetVars();
    fault = true;
  }
  else
  {
    pReg();
    checkRev();
  }
}


void enableTimers()
{
  TCCR1A |= ((1 << COM1A1) | (1 << COM1B1));
}  

void motorsBrake()
{
  PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
  PORTB &= ~(1 << 4);
  TCCR1A &= ~((1 << COM1A1) | (1 << COM1B1));
  PORTB |= ((1 << 5) | (1 << 6));
  OCR1A = 0;
  OCR1B = 0;
}

void motorsFloat()
{
  PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
  PORTB &= ~(1 << 4);
  TCCR1A &= ~((1 << COM1A1) | (1 << COM1B1));
  PORTB &= ~((1 << 5) | (1 << 6));
  OCR1A = 0;
  OCR1B = 0;
}

void resetVars()
{
  speed = 0;
  setPoint = 0;
  dist = 0;
  c0 = 0;
  c1 = 0; 
  completed = true;
}

void pReg()
{
  if(speed == 0) return;
  noInterrupts(); // Disable interrupts, no need to slow down the P regulator
  if(setPoint != 0)
  {
    output = map(setPoint, -100, 100, -speed, speed);
  }
  else
  {
    output = (duration0 - duration1) * p;
  }
  if(speed - output < 0) output = speed;
  if(speed + output < 0) output = -speed;
  //Serial.println(output,DEC);
  int temp;
  if(output >= 0) // its turning left of the setpoint, reduce pwm0 (right motor) pin 10 = OCR1B pin 11 = OCR2A
  {
    temp = speed - output;
    OCR1B = speed;
    OCR1A = temp; // Subtract the error value multiplied by Kp from pwm0
  }
  else // turning right of our setpoint, reduce pwm1
  {
    temp = speed + output;
    OCR1B = temp;
    OCR1A = speed;
  }
  duration0 = 0;
  duration1 = 0;
  interrupts(); //Enable interrupts again
}

void wheelSpeed0()
{
  duration0++;
  c0++;
}

void wheelSpeed1()
{
  duration1++;
  c1++;
}
