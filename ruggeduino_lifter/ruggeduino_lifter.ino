#include "LPD8806.h"
#include "SPI.h"
#include "TimerOne.h"

#define SERIAL_BAUD 115200
#define FW_VER "1"

#define encoder0PinA 2

#define encoder0PinB 3

#define taster 4

#define token 15000
#define drive 70000
#define top 95000

#define standbySpeed 3000.0
#define standbyColor strip.Color(val, val, val / 1.3)

#define attackSpeed 300.0
#define attackColor strip.Color(val, 0, 0)

#define idleSpeed 2000.0
#define idleColor strip.Color(val / 3, val, 0) // set a timer of length 100000 microseconds (or 0.1 sec - or 10Hz => the led will blink 5 times, 5 cycles of on-and-off, per second)

#define scoreSpeed 50.0
#define scoreColor i % 4 == 0 ? strip.Color(val, val, val) : strip.Color(0, val / 2, val)

LPD8806 strip = LPD8806(64);

volatile int val = 0.0;
volatile byte mode = 0; //0: standby, 1: idle, 2: attack, 3: score, 4: victory
float speed = 0.0;
volatile uint32_t color = 0;

volatile unsigned long encoder0Pos = 0;

volatile byte pos = 0;

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

// We communicate, by default, with the power board at 9200 baud.
void setup() {
  Serial.begin(SERIAL_BAUD);
  pinMode(encoder0PinA, INPUT);
  pinMode(encoder0PinB, INPUT);
  pinMode(taster, INPUT);
  digitalWrite(taster, HIGH);
    // encoder pin on interrupt 0 (pin 2)

  attachInterrupt(0, doEncoderA, CHANGE);

  // encoder pin on interrupt 1 (pin 3)

  attachInterrupt(1, doEncoderB, CHANGE); 
  
  strip.begin();
  
  // Update the strip, to start they are all 'off'
  strip.show();
  
  standby();
  
  Timer1.initialize(5000); // set a timer of length 100000 microseconds (or 0.1 sec - or 10Hz => the led will blink 5 times, 5 cycles of on-and-off, per second)
  Timer1.attachInterrupt(timerIsr); // attach the service routine here

}

void timerIsr()
{
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

int read_pin() {
  while (!Serial.available());
  int pin = Serial.read();
  return (int)(pin - 'a');
}

void command_read() {
  int pin = read_pin();
  // Read from the expected pin.
  int level = digitalRead(pin);
  // Send back the result indicator.
  if (level == HIGH) {
    Serial.write('h');
  } else {
    Serial.write('l');
  }
}

void command_analogue_read() {
  int pin = read_pin();
  if(pin == 10) Serial.print(pos);
  else {
    int value = analogRead(pin);
    Serial.print(value);
  }
}

void command_write(int level) {
  int pin = read_pin();
  digitalWrite(pin, level);
}

void command_mode(int mode) {
  int pin = read_pin();
  pinMode(pin, mode);
}

void leds()
{
  while(!Serial.available());
  char mode = Serial.read();
  switch(mode)
  {
    case 'o':
      standby();
      break;
    case 'i':
      idle();
      break;
    case 'a':
      attack();
      break;
    case 's':
      score();
      break;
  }
}

void loop() {
  // Fetch all commands that are in the buffer
  if (Serial.available()) {
    int selected_command = Serial.read();
    // Do something different based on what we got:
    switch (selected_command) {
      case 'a':
        command_analogue_read();
        break;
      case 'r':
        command_read();
        break;
      case 'l':
        command_write(LOW);
        break;
      case 'h':
        command_write(HIGH);
        break;
      case 'i':
        command_mode(INPUT);
        break;
      case 'o':
        command_mode(OUTPUT);
        break;
      case 'p':
        command_mode(INPUT_PULLUP);
        break;
      case 'b':
        leds();
        break;
      case 'v':
        Serial.print("MAIDuino:");
        Serial.print(FW_VER);
        break;
      default:
        // A problem here: we do not know how to handle the command!
        // Just ignore this for now.
        break;
    }
    Serial.print("\n");
  }
  
  if(digitalRead(taster) == LOW) {
    encoder0Pos = 0;
    pos = 0;
  }
  else {
    if(encoder0Pos >= token - 1700 && encoder0Pos <= token + 1700) pos = 1;
    else if(encoder0Pos >= drive - 1700 && encoder0Pos <= drive + 7500) pos = 2;
    else if(encoder0Pos >= top && encoder0Pos <= top + 7000) pos = 3;
    else pos = 4;
  }
}

void doEncoderA(){

  // look for a low-to-high on channel A
  if (digitalRead(encoder0PinA) == HIGH) {

    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == LOW) {
      encoder0Pos = encoder0Pos + 1; // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1; // CCW
    }
  }

  else // must be a high-to-low edge on channel A
  {
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == HIGH) {
      encoder0Pos = encoder0Pos + 1; // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1; // CCW
    }
  }
  //Serial.println (encoder0Pos, DEC);
  // use for debugging - remember to comment out

}

void doEncoderB(){

  // look for a low-to-high on channel B
  if (digitalRead(encoder0PinB) == HIGH) {

    // check channel A to see which way encoder is turning
    if (digitalRead(encoder0PinA) == HIGH) {
      encoder0Pos = encoder0Pos + 1; // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1; // CCW
    }
  }

  // Look for a high-to-low on channel B

  else {
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinA) == LOW) {
      encoder0Pos = encoder0Pos + 1; // CW
    }
    else {
      encoder0Pos = encoder0Pos - 1; // CCW
    }
  }
}
