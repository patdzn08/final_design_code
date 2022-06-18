#include <AccelStepper.h>
#include <MultiStepper.h>

int command;
#define dirPin 4
#define stepPin 5
#define enablePin 6
#define stepsPerRevolution 75
#define motorInterfaceType 1
int Valve = 11;
bool is_conveyor_active = false;

// Create a new instance of the AccelStepper class:
AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);

// Activate valve function
void valve () {
  digitalWrite(Valve,HIGH);
  delay(1000);
  digitalWrite(Valve,LOW);
  delay(1000);
}

// Activate conveyor function
void conveyor () {
  digitalWrite(dirPin, LOW);
  for (int i = 0; i < 1 * stepsPerRevolution; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(5500); //speed up or down
    digitalWrite(stepPin, LOW);
    delayMicroseconds(5500); //spped up or down
  }
  delay(500);
}

// Setup function
void setup () {
  pinMode(stepPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(Valve,OUTPUT);
  digitalWrite(enablePin,LOW);
  stepper.setMaxSpeed(-1000); // Set the maximum speed in steps per second
  Serial.begin(9600);
}

// Loop function
void loop () {
  command = 0;
   // Check received data
   if (Serial.available() > 0) {
    command = Serial.read(); // Get received data and store to command variable
    if (command == 1) {
      Serial.write(1);
    } else if (command == 2) {
      Serial.write(2);
      is_conveyor_active = true;
    } else if (command == 3) {
      Serial.write(3);
      is_conveyor_active = false;
    }
   }
   // Check the command
    if (command == 1) {
      valve(); // Call valve function
    } else  {
      if (is_conveyor_active == true) {
        conveyor(); // Call conveyor function
      } 
      else if (is_conveyor_active == false) {
        stepper.stop(); // Stop the conveyor
      }
    }
}
