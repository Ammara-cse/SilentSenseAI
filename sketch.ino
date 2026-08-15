#include "Arduino_RouterBridge.h"

int pirPin = 7;        // PIR OUT D7
int ledPin = 8;        // LED / Buzzer pin D8
int panicPin = 4;      // Panic Button D4 (Connect Pin 4 and GND)

unsigned long lastMotionTime = 0;      // Stores last motion timestamp
const unsigned long delayTime = 30000; // 30 seconds delay
bool motionDetected = false;
bool panicPressed = false;             // Stores panic button state

// Functions exposed to Python via Bridge
int get_motion() {
    return motionDetected ? 1 : 0;
}

int get_panic() {
    return panicPressed ? 1 : 0;
}

void setup() {
  pinMode(pirPin, INPUT);
  pinMode(panicPin, INPUT_PULLUP); // Internal pullup for Panic Button
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, HIGH); // LED ON = No motion
  
  // Initialize Bridge communication with Python container
  Bridge.begin();
  Bridge.provide_safe("get_motion", get_motion);
  Bridge.provide_safe("get_panic", get_panic);
  
  delay(10000); // PIR sensor stabilization delay
}

void loop() {
  // 1. Panic Button Logic
  if (digitalRead(panicPin) == LOW) { // Button pressed
    panicPressed = true;
    digitalWrite(ledPin, HIGH);       // Light / Buzzer ON immediately on panic
  } else {
    panicPressed = false;
  }

  // 2. Original Motion Logic
  int pirVal = digitalRead(pirPin);

  if (pirVal == HIGH) {   // Motion detected
    digitalWrite(ledPin, LOW);    // LED OFF
    lastMotionTime = millis();    // Reset 30s timer
    motionDetected = true;
  } 
  else { // No motion
    if (motionDetected && (millis() - lastMotionTime >= delayTime)) {
      digitalWrite(ledPin, HIGH);   // LED ON after 30s
      motionDetected = false;
    }
  }

  delay(100);
}