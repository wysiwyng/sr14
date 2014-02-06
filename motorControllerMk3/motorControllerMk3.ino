#include "wiring_private.h"
#include "pins_arduino.h"


#define pi 3.14159265


#define encoder0pinA 3

#define encoder1pinA 2


#define dir0A 12    //PD6
#define dir0A_on (PORTD |= (1 << 6))
#define dir0A_off (PORTD &= ~(1 << 6))

#define dir0B 4     //PD4
#define dir0B_on (PORTD |= (1 << 4))
#define dir0B_off (PORTD &= ~(1 << 4))

#define dir1A 8     //PB4
#define dir1A_on (PORTB |= (1 << 4))
#define dir1A_off (PORTB &= ~(1 << 4))

#define dir1B 6     //PD7
#define dir1B_on (PORTD |= (1 << 7))
#define dir1B_off (PORTD &= ~(1 << 7))

#define pwm0 9
#define pwm1 10

#define wheelDiameter 9
#define wheelDistance 41.5
#define cpr 1600

#define cpcm cpr/(wheelDiameter*pi)
#define cmpd (wheelDistance*pi)/360

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

  attachInterrupt(0, wheelSpeed0, CHANGE);
  attachInterrupt(1, wheelSpeed1, CHANGE);

  TIMSK3 |= (1<<TOIE1); // Enable Timer1 overflow interrupt at 16MHz = 16 000 000 / 2^16 = 244Hz

  byte lamps[4] = {
    dir0A,dir0B,dir1A,dir1B  };
  byte j = 0;
  boolean temp = LOW;

  while(!Serial)
  {
    digitalWrite(lamps[j],temp);
    if(j<4) j++;
    else {
      j=0;
      temp = !temp;
    }
    delay(100);
  }

  //Serial.write(104);

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
    cbi(TCCR1A, COM1A1);
    cbi(TCCR1A, COM1B1);
    PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
    PORTB &= ~(1 << 4);
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

void loop()
{
  if(Serial.available()>5 && Serial.read()=='$')
  {
    byte instruction = Serial.read();
    if(bitRead(instruction, 7) == 1 && bitRead(instruction, 6) == 1 && bitRead(instruction, 5) == 0 && bitRead(instruction, 4) == 1 && bitRead(instruction, 3) == 1)
    {
      uint8_t _speed = Serial.read();
      int8_t _direction = Serial.read();
      uint16_t _distance = word(Serial.read(), Serial.read());
      boolean f = bitRead(instruction,2);
      boolean turn = bitRead(instruction,1);
      boolean brake = bitRead(instruction,0);

      if(_distance > 0 && _distance < 5)
      {
        _distance = 5;
      }

      if(brake)
      {
        cbi(TCCR1A, COM1A1);
        cbi(TCCR1A, COM1B1);
        PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
        PORTB &= ~(1 << 4);
        PORTB |= ((1 << 5) | (1 << 6));
        setParams();
      }
      else if(_speed == 0)
      {
        cbi(TCCR1A, COM1A1);
        cbi(TCCR1A, COM1B1);
        PORTD &= ~((1 << 4) | (1 << 6) | (1 << 7));
        PORTB &= ~((1 << 4) | (1 << 5) | (1 << 6));
        setParams();
      }
      else if(turn && f)
      {
        PORTD |= (1 << 4);
        PORTD &= ~((1 << 6) | (1 << 7));
        PORTB |= (1 << 4);
        setParams(_speed, 0, _distance * cmpd);
      }
      else if(turn)
      {
        PORTD &= ~(1 << 4);
        PORTD |= ((1 << 6) | (1 << 7));
        PORTB &= ~(1 << 4);
        setParams(_speed, 0, _distance * cmpd);
      }
      else if(f)
      {
        PORTD &= ~(1 << 6);
        PORTD |= ((1 << 4) | (1 << 7));
        PORTB &= ~(1 << 4);
        setParams(_speed, _direction, _distance);
      }
      else if (!f)
      {
        PORTD |= (1 << 6);
        PORTD &= ~((1 << 4) | (1 << 7));
        PORTB |= (1 << 4);
        setParams(_speed, _direction, _distance);
      }

      if(_distance > 0) completed = false;
      fault = false;

      while(!completed) {
      }

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

ISR(TIMER3_OVF_vect) //timer interupt routine
{
  overflow++;
  if(overflow>=10)
  {
    if((duration0 < 15 || duration1 < 15) && speed > 0)
    {
      faultCount++;
    }
    if(faultCount > 7)
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
  if(output >= 0) // its turning left of the setpoint, reduce pwm0 (right motor) pin 10 = OCR1B pin 11 = OCR2A
  {
    analogWrite(pwm1, speed);
    analogWrite(pwm0, (speed-output)); // Subtract the error value multiplied by Kp from pwm0
  }
  if(output < 0) // turning right of our setpoint, reduce pwm1
  {
    analogWrite(pwm1, (speed+output)); // This time we add the error since its negative
    analogWrite(pwm0, speed);
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

