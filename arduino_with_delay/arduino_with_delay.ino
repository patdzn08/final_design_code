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

// Activate valve
void valve()
{
  digitalWrite(Valve,HIGH);
  delay(1000);
  digitalWrite(Valve,LOW);
  delay(1000);
}

// Activate conveyor
void conveyor()
{
//  digitalWrite(dirPin, LOW);
//  for (int i = 0; i < 1 * stepsPerRevolution; i++)
//  {
//    digitalWrite(stepPin, HIGH);
//    delayMicroseconds(1400); //speed up or down
//    digitalWrite(stepPin, LOW);
//    delayMicroseconds(1400); //spped up or down 
//  }
//  delay(800);
  // Set the speed in steps per second:
  stepper.setSpeed(-100);
  // Step the motor with a constant speed as set by setSpeed():
  stepper.runSpeed();
}

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(Valve,OUTPUT);
  digitalWrite(enablePin,LOW);
  // Set the maximum speed in steps per second:
  stepper.setMaxSpeed(-1000);
  Serial.begin(9600);

}

void loop() {
   // Check received data
   if (Serial.available() > 0)
   {
    command = Serial.read(); // Get received data and store to command variable
    if (command == 0x02)
    {
      if (is_conveyor_active == false)
      {
        is_conveyor_active = true;
      } 
      else if (is_conveyor_active == true)
      {
        is_conveyor_active = false;
      }
    }
   }
   // Check the command
    if (command == 1)
    {
      delay(1000);
      valve(); // Call valve function
    }
    else
    {
      if (is_conveyor_active == true)
      {
        conveyor(); // Call conveyor function 
      }
      else
      {
        delay(500);
        stepper.stop(); // Stop the stepper motor
      }
    }
}
