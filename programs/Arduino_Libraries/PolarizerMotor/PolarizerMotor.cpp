/* 
 * PolarizerMotor.h - Library to control the Parallax Feedback 360� High-Speed Servo,
 *                    and mainly used to rotate the polarizer in the S15 EKPQC kit.
 * Version 0.2 
 * Author: Adrian Utama 
 *
 * The servo motor uses a nominal 6V power supply. The rotation speed is set by tuning  
 * the PWM pulse in the controlPin. The current angle can be read using the PWM pulse of 
 * the feedbackPin. With these, one can set a feedback loop to control the angle.
 */
 
#include "Arduino.h"
#include <Servo.h>
#include "PolarizerMotor.h"

// constructor
PolarizerMotor::PolarizerMotor(int controlPin, int feedbackPin, int anglePrecision)
{
  this->controlPin = controlPin;
  this->feedbackPin = feedbackPin;
  this->anglePrecision = anglePrecision;
}

// method to initialize, in the setup version of the code
void PolarizerMotor::initialize()
{
  // Attach the control signal
  controlSignal.attach(controlPin);
  // Read the initial angle
  this->currentAngle = readAngle();  
}

// method to read the current angle. Note: each call uses noInterrupt routine for ~2 ms.
float PolarizerMotor::readAngle()
{
  unsigned long highTime, lowTime;
  unsigned long totalTime;
  float dutyCycle, angle;

  while (1){
    noInterrupts();
    highTime = pulseIn(this->feedbackPin, HIGH);
    lowTime = pulseIn(this->feedbackPin, LOW);
    interrupts();
    totalTime = highTime + lowTime;
    // to check whether time is within acceptable range
    if (totalTime > this->feedbackMinPeriod and 
        totalTime < this->feedbackMaxPeriod) break; 
  }
  
  dutyCycle = float(highTime) / totalTime;
  angle = (dutyCycle - this->feedbackMinDC) * 360 / 
          (this->feedbackMaxDC - this->feedbackMinDC); // in degrees
  
  // Bound the angle to be within 0 and 360 degrees
  if (angle < 0  ) angle = 0;
  if (angle > 360) angle = 360;
  
  // Update the currentAngle
  this->currentAngle = angle;
    
  return angle;
}

void PolarizerMotor::setSpeed(int speed)
{
  // Bound the speed in both directions
  if (speed > this->controlMaxSpeed) {
    this->motorSpeed = this->controlMaxSpeed;
  } else if (speed < - this->controlMaxSpeed) {
    this->motorSpeed = - this->controlMaxSpeed;
  } else {
    this->motorSpeed = speed;
  }
  
  int pulseLength = this->controlPulseOffset + this->rotationPolarity * this->motorSpeed; 
  this->controlSignal.writeMicroseconds(pulseLength); // set the motor in motion
}

void PolarizerMotor::gotoAngle(int targetAngle, int wrap)
{
  float currentAngle;
  float deltaAngle;
  // Serial.println("Calling gotoAngle");
  // Moving until target achieved
  while (1){
    // Get the deltaAngle to move
    currentAngle = readAngle();
    deltaAngle = targetAngle - currentAngle;
    
    // Wrap the angular movement. If the delta angle is more than 180 degrees, go the other way
    if (wrap){
      if (deltaAngle > 180)  deltaAngle -= 360;
      if (deltaAngle < -180) deltaAngle += 360;
    }
    
    // Break loop if target precision achieved
    if (deltaAngle < this->anglePrecision and deltaAngle > -this->anglePrecision) {
      setSpeed(0); 
      break;
    }
    
    // Set speed if target angle not achieved
    if (deltaAngle > 0) 
      setSpeed(0.5*deltaAngle + this->cLoopSpeedOffset); // positive values
    else
      setSpeed(0.5*deltaAngle - this->cLoopSpeedOffset); // negative values
    
    // Wait until next cycle
    delay(this->controlPWMperiod);
  }
  this->controlSignal.writeMicroseconds(0);
}

float PolarizerMotor::gotoAngleAndChop(int targetAngle, int wrap, int checkAgain)
{
  float currentAngle;
  float deltaAngle;
  float doAgain;
  
  while (1)
  {
    // attempt movement
    gotoAngle(targetAngle, wrap);
    doAgain = 0;
    
    // check for checkAgain tries cycles
    for (int i=0; i<checkAgain; i++){
      // find deltaAngle
      currentAngle = readAngle();
      deltaAngle = targetAngle - currentAngle;
      
      // see whether it is outside precision
      if (deltaAngle > this->anglePrecision or deltaAngle < -this->anglePrecision) {
        doAgain = 1;  // then we do again
      }
      
      // delay until next cycle
      delay(this->controlPWMperiod);
    }

    // check the status of doAgain 
    if (doAgain == 0){
      break;
    }
  }
  this->controlSignal.writeMicroseconds(0);
  return readAngle();
}

float PolarizerMotor::approachAngle(int targetAngle, int wrap, int steps)
{
  float currentAngle;
  float deltaAngle;

  float startTime = millis();
  float timeNow = startTime;
  float timeStep;
  // Serial.println("Calling approachAngle");
  // Moving for the number of steps
  for (int i = 0; i < steps; i++)
  {
    timeStep = startTime + i * this->controlPWMperiod; 
    // Wait until next cycle
    while(timeNow < timeStep){
      timeNow = millis();     // Keep checking the time
    }

    // Get the deltaAngle to move
    currentAngle = readAngle();
    deltaAngle = targetAngle - currentAngle;
 
    // Wrap the angular movement. If the delta angle is more than 180 degrees, go the other way
    if (wrap){
      if (deltaAngle > 180)  deltaAngle -= 360;
      if (deltaAngle < -180) deltaAngle += 360;
    }
        
    // Set speed to approach the target
    if (deltaAngle > 0) 
      setSpeed(deltaAngle + this->cLoopSpeedOffset); // positive values
    else
      setSpeed(deltaAngle - this->cLoopSpeedOffset); // negative values
    
  }
  
  setSpeed(0);
  this->controlSignal.writeMicroseconds(0);
  currentAngle = readAngle();
  return currentAngle;
}
