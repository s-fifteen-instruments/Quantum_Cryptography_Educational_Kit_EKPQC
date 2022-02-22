/* Parallax Motor Testing Sandbox 
 * Just to test some functionalities of the motor
 * Author: Adrian Utama
 */

#include <Servo.h>

// Important parameters
const int pinMotorControl = 8;
const int pinMotorFeedback = 9;

// Other parameters
unsigned long optime;
float currentAngle;

Servo motor; // to control the motor

float readMotorAngle() {
  unsigned long highTimeFb, lowTimeFb;
  unsigned long totalTimeFb;
  float dutyCycle, angle;

  while (1){
    noInterrupts();
    highTimeFb = pulseIn(pinMotorFeedback, HIGH);
    lowTimeFb = pulseIn(pinMotorFeedback, LOW);
    interrupts();
    totalTimeFb = highTimeFb + lowTimeFb;
    // to check whether time is within acceptable range
    if (totalTimeFb>1000 and totalTimeFb<1200) break; 
  }
  
  dutyCycle = float(highTimeFb) / totalTimeFb;
  angle = (dutyCycle - 0.029)*360 / (0.971-0.029); // for Parallax 900-00360
  return angle;
}

void setMotorSpeed(int speed){
  //Serial.write("speed\t");
  //Serial.println(speed);
  if (speed > 220) speed=220;
  if (speed <-220) speed=-220;
  motor.writeMicroseconds(speed+1500); // for Parallax 900-00360
}

void gotoMotorAngle(float targetAngle){
  float currentAngle = readMotorAngle();
  float deltaAngle = currentAngle - targetAngle;
  float currentTime = millis();
  while (1){
    currentAngle = readMotorAngle();
    deltaAngle = currentAngle - targetAngle;
    //Serial.print("offset");
    //Serial.print(millis()-currentTime);
    //Serial.write("\t");
    //Serial.println(currentAngle);
    //Serial.write("\t");
    //Serial.println(deltaAngle);
    // Break loop if target achieved
    if (deltaAngle < 5 and deltaAngle > -5) {
      setMotorSpeed(0); 
      break;
    }
    // Set speed if target not achieved
    if (deltaAngle > 0)
      setMotorSpeed(deltaAngle+30);
    else
      setMotorSpeed(deltaAngle-30);
    delay(20);

  }
  Serial.print("achieved");
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(38400); // For debugging, with higher speed
  motor.attach(pinMotorControl);
  motor.writeMicroseconds(1600);
  setMotorSpeed(50);
  delay(1000);
}

void loop() {
  char valbuf[8] = "";
  while (!Serial.available());
  Serial.readBytesUntil(' ', valbuf, 8);
  int targetAngle = atoi(valbuf);
  //Serial.print("target Angle: ");
  //Serial.println(targetAngle);
  float currentAngle;
  gotoMotorAngle(targetAngle);
  delay(100);
  Serial.print("outside ");
  Serial.println(readMotorAngle());
  delay(1000);
}
