#include "wiring_private.h"
#include "pins_arduino.h"
#include <TimerThree.h>

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
#define wheelDistance 45
#define cpr 1600

#define cpcm cpr/(wheelDiameter*pi)
#define cmpd (wheelDistance*pi)/360

#define maxFaults 20
#define minSpeed 5

word c0;
word c1;

double dist;

byte overflow;

int duration0;//Encoder0 number of pulses
int duration1;//Encoder1 number of pulses

int setPoint = 0; // 0 would be straight ahead
double p = 10; // needs tuning
int error = 0;
int speed = 0; // set the speed of which the vechicle should move
int output = 0;

volatile int faultCount = 0;

volatile boolean completed = true;
volatile boolean fault = false;
volatile boolean preFault = false;

//ISR(TIMER3_OVF_vect) //timer interupt routine
void timer3_int()
{
  overflow++;
  if(overflow>=10)
  {
    if((duration0 < minSpeed || duration1 < minSpeed) && speed > 0)
    {
      if(preFault) faultCount++;
      else preFault = true;
    }
    else preFault = false;
    if(faultCount > maxFaults)
    {
      cbi(TCCR1A, COM1A1);
      cbi(TCCR1A, COM1B1);
      PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
      PORTB &= ~(1 << 4);
      PORTB |= ((1 << 5) | (1 << 6));
      speed = 0;
      setPoint = 0;
      dist = 0;
      completed = true;
      fault = true;
      c0 = 0;
      c1 = 0;
      faultCount = 0;
    }
    else
    {
      pReg(duration0, duration1);
      checkRev();
      duration0=0;
      duration1=0;
      overflow=0;
    }
  }
}

void setup()
{
  pinMode(pwm0, OUTPUT);
  pinMode(pwm1, OUTPUT);
  pinMode(dir0A, OUTPUT);
  pinMode(dir0B, OUTPUT);
  pinMode(dir1A, OUTPUT);
  pinMode(dir1B, OUTPUT);

  motor0float();
  motor1float();

  Serial.begin(115200); //Initialize the serial port
#ifdef debug
  Serial1.begin(115200);
#endif
  attachInterrupt(0, wheelSpeed0, CHANGE);
  attachInterrupt(1, wheelSpeed1, CHANGE);

  Timer3.initialize(2000);
  Timer3.attachInterrupt(timer3_int);
  Timer3.start();
  byte lamps[4] = {
    dir0A,dir0B,dir1A,dir1B      };
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
  motor0stop();
  motor1stop();
}

void setParams(uint8_t spd = 0, int8_t dir = 0, word distance = 0)
{
  c0=0;
  c1=0;
  speed = spd;
  setPoint = dir;
  dist = distance;
}

void checkRev()
{
  if(dist==0 || speed==0) {
    return;
  }
  noInterrupts();
  if(c0 >= (dist*cpcm) || c1 >= (dist*cpcm))
  {
    PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
    PORTB &= ~(1 << 4);
    cbi(TCCR1A, COM1A1);
    cbi(TCCR1A, COM1B1);
    PORTB |= ((1 << 5) | (1 << 6));
    speed = 0;
    setPoint = 0;
    dist = 0;
    completed = true;
    fault = false;
    c0 = 0;
    c1 = 0;
  }
  interrupts();
}

byte counter = 0;
byte vars[5] = {
  0, 0, 0, 0, 0};

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
      uint8_t _speed = vars[1];
      int8_t _direction = vars[2];
      uint16_t _distance = word(vars[3], vars[4]);
      boolean f = bitRead(instruction,2);
      boolean turn = bitRead(instruction,1);
      boolean brake = bitRead(instruction,0); 
#ifdef debug
      Serial1.println("complete command received");
      Serial1.println(instruction);
      Serial1.println(_speed);
      Serial1.println(_direction);
      Serial1.println(_distance);
#endif
      if(_distance > 0 && _distance < 5)
      {
        _distance = 5;
      }

      if(brake)
      {
        PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
        PORTB &= ~(1 << 4);
        cbi(TCCR1A, COM1A1);
        cbi(TCCR1A, COM1B1);
        PORTB |= ((1 << 5) | (1 << 6));
        setParams();
      }
      else if(_speed == 0)
      {
        PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
        PORTB &= ~(1 << 4);
        cbi(TCCR1A, COM1A1);
        cbi(TCCR1A, COM1B1);
        PORTB &= ~((1 << 5) | (1 << 6));
        setParams();
      }
      else if(turn && f)
      {
        PORTD |= (1 << 4);
        PORTD &= ~((1 << 6) | (1 << 7));
        PORTB |= (1 << 4);
        setParams(_speed, 0, _distance * cmpd);
        sbi(TCCR1A, COM1A1);
        sbi(TCCR1A, COM1B1);
      }
      else if(turn)
      {
        PORTD &= ~(1 << 4);
        PORTD |= ((1 << 6) | (1 << 7));
        PORTB &= ~(1 << 4);
        setParams(_speed, 0, _distance * cmpd);
        sbi(TCCR1A, COM1A1);
        sbi(TCCR1A, COM1B1);
      }
      else if(f)
      {
        PORTD &= ~(1 << 6);
        PORTD |= ((1 << 4) | (1 << 7));
        PORTB &= ~(1 << 4);
        setParams(_speed, _direction, _distance);
        sbi(TCCR1A, COM1A1);
        sbi(TCCR1A, COM1B1);
      }
      else if (!f)
      {
        PORTD |= (1 << 6);
        PORTD &= ~((1 << 4) | (1 << 7));
        PORTB |= (1 << 4);
        setParams(_speed, _direction, _distance);
        sbi(TCCR1A, COM1A1);
        sbi(TCCR1A, COM1B1);
      }

      if(_distance > 0) completed = false;
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
      Serial.write(_speed);
      Serial.write(_direction);
      Serial.write(highByte(_distance));
      Serial.write(lowByte(_distance));
    }
  }
}

void motor0stop()
{
  dir0A_off;
  dir0B_off;
  digitalWrite(pwm0,HIGH);
}

void motor0float()
{
  dir0A_off;
  dir0B_off;
  digitalWrite(pwm0,LOW);
}

void motor1stop()
{
  dir1A_off;
  dir1B_off;
  digitalWrite(pwm1,HIGH);
}

void motor1float()
{
  dir1A_off;
  dir1B_off;
  digitalWrite(pwm1,LOW);
}

void pReg(int speedL, int speedR)
{
  if(speed == 0) return;
  noInterrupts(); // Disable interrupts, no need to slow down the P regulator
  if(setPoint != 0)
  {
    output = map(setPoint, -100, 100, -speed, speed);
  }
  else
  {
    output = (speedL - speedR) * p;
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
  if(output < 0) // turning right of our setpoint, reduce pwm1
  {
    temp = speed + output;
    OCR1B = temp;
    OCR1A = speed;
  }
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



