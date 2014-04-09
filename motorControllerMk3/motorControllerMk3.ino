#include <TimerThree.h>
#include <avr/wdt.h>
#include <SoftwareSerial.h>

#define debug

#define VERSION 132

#define pi 3.14159265

#define encoder0pinA PIN_D0
#define encoder1pinA PIN_D1

#define dir0A PIN_D6     //PD6
#define dir0B PIN_D4     //PD4

#define dir1A PIN_B4     //PB4
#define dir1B PIN_D7     //PD7

#define pwm0 PIN_B5
#define pwm1 PIN_B6

#define wheelDiameter 11
#define wheelDistance 46
#define cpr 1600

#define cpcm cpr/(wheelDiameter*pi)
#define cmpd (wheelDistance*pi)/360

#define maxFaults 40
#define minSpeed 10

volatile unsigned long c0 = 0;
volatile unsigned long c1 = 0;

volatile unsigned long dist = 0;

byte duration0 = 0;//Encoder0 number of pulses
byte duration1 = 0;//Encoder1 number of pulses

char setPoint = 0; // 0 would be straight ahead
#define p 10 // needs tuning
char error = 0;
byte speed = 0; // set the speed of which the vechicle should move
int output = 0;

byte faultCount = 0;

volatile byte status = 0;

#define get_completed status & (1 << 0)
#define get_fault status & (1 << 1)
#define get_preFault status & (1 << 2)
#define get_wait status & (1 << 3)
#define get_off status & (1 << 4)

#define set_completed status |= (1 << 0)
#define set_fault status |= (1 << 1)
#define set_preFault status |= (1 << 2)
#define set_wait status |= (1 << 3)
#define set_off status |= (1 << 4)

#define reset_completed status &= ~(1 << 0)
#define reset_fault status &= ~(1 << 1)
#define reset_preFault status &= ~(1 << 2)
#define reset_wait status &= ~(1 << 3)
#define reset_off status &= ~(1 << 4)

byte counter = 0;
byte vars[5] = {
  0, 0, 0, 0, 0};

SoftwareSerial debugSer(MISO, MOSI); //rx tx

void setup()
{
  MCUSR &= ~(1 << WDRF);
  wdt_disable();

  DDRD |= ((1 << 4) | (1 << 6) | (1 << 7));
  DDRB |= ((1 << 4) | (1 << 5) | (1 << 6));

  PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
  PORTB &= ~((1 << 4) | (1 << 5) | (1 << 6));

  Serial.begin(115200); //Initialize the serial port

#ifdef debug
  debugSer.begin(9600);
#endif

  attachInterrupt(0, wheelSpeed0, CHANGE);
  attachInterrupt(1, wheelSpeed1, CHANGE);

  Timer3.initialize(20000);
  Timer3.attachInterrupt(timer3_int);
  Timer3.start();

  PORTD |= ((1 << 4) | (1 << 6) | (1 << 7));
  PORTB |= (1 << 4);
  delay(500);
  PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
  PORTB &= ~(1 << 4);

#ifdef debug
  debugSer.println("ready");
#endif

  PORTB |= ((1 << 5) | (1 << 6));
}

void loop()
{
  if(debugSer.available())
  {
    byte rec = debugSer.read();
    if(rec == 's')
    {
      speed = 0;
      motorsBrake();
    }
    else
    {
      enableTimers();
      switch(rec)
      {
      case 'w':
        speed = 255;
        PORTD &= ~(1 << 6);
        PORTD |= ((1 << 4) | (1 << 7));
        PORTB &= ~(1 << 4);
        break;
      case 'x':
        speed = 255;
        PORTD |= (1 << 6);
        PORTD &= ~((1 << 4) | (1 << 7));
        PORTB |= (1 << 4);
        break;
      case 'a':
        speed = 130;
        PORTD &= ~(1 << 4);
        PORTD |= ((1 << 6) | (1 << 7));
        PORTB &= ~(1 << 4);
        break;
      case 'd':
        speed = 130;
        PORTD |= (1 << 4);
        PORTD &= ~((1 << 6) | (1 << 7));
        PORTB |= (1 << 4);
        break;
      }
    }
  }
  if(Serial.available())
  {
    byte rec = Serial.read();

#ifdef debug
    debugSer.print("in:");
    debugSer.print(rec);
    debugSer.print("\rc:");
    debugSer.print(counter);
    debugSer.print("\r");
#endif

    if(counter == 0)
    {
      switch(rec)
      {
      case 'v':
        Serial.write(VERSION);
        break;
      case '$':
        counter = 1;
        break;
      }
    }
    else if(counter > 0)
    {
      vars[counter - 1] = rec;
      counter++;
    }
    if(counter == 6)
    {
      counter = 0;
      speed = vars[1];
      setPoint = vars[2];

#ifdef debug
      debugSer.print("compl\r");
      debugSer.print(vars[0]);
      debugSer.print("\r");
      debugSer.print(speed);
      debugSer.print("\r");
      debugSer.print(setPoint);
      debugSer.print("\r");
      debugSer.print(word(vars[3], vars[4]));
      debugSer.print("\r");
#endif

      if(vars[0] & (1 << 0))
      {
        motorsBrake();
      }
      else if(speed == 0)
      {
        motorsFloat();
      }
      else 
      {
        if(vars[0] & (1 << 1))
        {
          dist = word(vars[3], vars[4]);
          dist = dist * cmpd;
          if(dist < 1 && word(vars[3], vars[4]) > 0) dist = 1;
          setPoint = 0;
          if(vars[0] & (1 << 2))
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
          if(vars[0] & (1 << 2))
          {
            PORTD &= ~(1 << 6);
            PORTD |= ((1 << 4) | (1 << 7));
            PORTB &= ~(1 << 4);
          }
          else if (!(vars[0] & (1 << 2)))
          {
            PORTD |= (1 << 6);
            PORTD &= ~((1 << 4) | (1 << 7));
            PORTB |= (1 << 4);
          }
        }
        enableTimers();
        c0 = 0;
        c1 = 0;
      }

      if(dist > 0) reset_completed;
      else set_completed;

      set_wait;
      reset_fault;

#ifdef debug
      debugSer.print("wait\r");
#endif
    }
  }
  if(!get_completed && get_wait)
  {
    checkRev();
  }
  else if(get_completed && get_wait)
  {
#ifdef debug
    debugSer.print("done\r");
#endif
    Serial.print('$');
    if(get_fault) bitClear(vars[0], 3);
    Serial.write(vars[0]);
    Serial.write(vars[1]);
    Serial.write(vars[2]);
    Serial.write(vars[3]);
    Serial.write(vars[4]);
    reset_wait;
  }
}

void checkRev()
{
  if(dist == 0 || speed == 0)
  {
    return;
  }
  if(c0 >= (dist * cpcm) || c1 >= (dist * cpcm))
  {
    motorsBrake();
    resetVars();
  }
}

void timer3_int()
{
  if((duration0 < minSpeed || duration1 < minSpeed) && speed > 0)
  {
    if(get_preFault) faultCount++;
    else 
    {
      set_preFault;
      faultCount = 0;
    }
  }
  else reset_preFault;

  if(faultCount > maxFaults)
  {
    motorsBrake();
    resetVars();
    faultCount = 0;
    set_fault;
  }
  else
  {
    pReg();
    checkRev();
  }
}

void enableTimers()
{
  reset_off;
  TCCR1A |= ((1 << COM1A1) | (1 << COM1B1));
}  

void motorsBrake()
{
  motorsOff();
  PORTB |= ((1 << 5) | (1 << 6));
  OCR1A = 0;
  OCR1B = 0;
}

void motorsFloat()
{
  motorsOff();
  PORTB &= ~((1 << 5) | (1 << 6));
  OCR1A = 0;
  OCR1B = 0;
}

void motorsOff()
{
  if(get_off) return;
  set_off;
  if((PORTD & 0xC0) == 0xC0) PORTD &= ~0xC0;
  else if((PORTD & 0x90) == 0x90) PORTD &= ~0x90;
  else if((PORTD & 0xC0) == 0) PORTD |= 0xC0;
  else if((PORTD & 0x90) == 0) PORTD |= 0x90;
  TCCR1A &= ~((1 << COM1A1) | (1 << COM1B1));
}

void resetVars()
{
  speed = 0;
  setPoint = 0;
  dist = 0;
  set_completed;
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


