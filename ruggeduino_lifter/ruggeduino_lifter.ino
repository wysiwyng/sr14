#define SERIAL_BAUD 115200
#define FW_VER "1"

#define encoder0PinA 2

#define encoder0PinB 3

#define taster 4

#define token 15000
#define drive 70000
#define top 95000

volatile unsigned long encoder0Pos = 0;

volatile byte pos = 0;

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

void loop() {
  // Fetch all commands that are in the buffer
  while (Serial.available()) {
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
      case 'v':
        Serial.print("SRduino:");
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
