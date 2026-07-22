/*
 * SilentSense AI — Physical AI Firmware
 * Board: Arduino® UNO™ Q
 * Team: AFS Synaptic Edge
 * Contest: Arduino Physical AI Challenge India 2026
 */

const int PIR_PIN = 2;       // Motion Sensor Pin
const int LDR_PIN = A0;      // Light Sensor Pin
const int BUZZER_PIN = 8;    // Local Physical Alarm Pin

void setup() {
  Serial.begin(9600);
  pinMode(PIR_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  int motionDetected = digitalRead(PIR_PIN);
  int lightLevel = analogRead(LDR_PIN);
  
  bool isLightOn = (lightLevel > 400);

  // Send JSON Telemetry over Serial to Python Engine
  Serial.print("{\"motion\": ");
  Serial.print(motionDetected == HIGH ? "true" : "false");
  Serial.print(", \"light_on\": ");
  Serial.print(isLightOn ? "true" : "false");
  Serial.println("}");

  delay(2000); 
}