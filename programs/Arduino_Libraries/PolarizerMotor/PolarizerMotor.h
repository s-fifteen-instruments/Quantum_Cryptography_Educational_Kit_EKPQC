/* 
 * PolarizerMotor.h - Library to control the Parallax Feedback 360° High-Speed Servo,
 *                    and mainly used to rotate the polarizer in the S15 EKPQC kit.
 * Version 0.2 
 * Author: Adrian Utama 
 *
 * The servo motor uses a nominal 6V power supply. The rotation speed is set by tuning  
 * the PWM pulse in the controlPin. The current angle can be read using the PWM pulse of 
 * the feedbackPin. With these, one can set a feedback loop to control the angle.
 */
 
// requires servo library (for the control signal) 
#include <Servo.h>
 
// include guard
#ifndef PolarizerMotor_h
#define PolarizerMotor_h 
 
class PolarizerMotor {
  public:
    // constructor 
    PolarizerMotor(int controlPin, int feedbackPin, int anglePrecision = 5);
    
    // method to initialize with no in the setup portion of the Arduino code. Important! 
    void initialize();
    
    // method to read the current angle. Note: each call uses noInterrupt routine for ~2 ms.
    float readAngle(); 
    
    // method to set the motor speed.        
    void setSpeed(int speed);  
    
    // method to move to the target angle - might overshoot (precision not guaranteed). 
    void gotoAngle(int targetAngle, int wrap=1); 
    
    // extension of gotoAngle(), where the angle is re-checked for checkAgain times with 
    // the motor set stationary, to ensure precision. Returns the value of last angle.
    float gotoAngleAndChop(int targetAngle, int wrap=1, int checkAgain = 5);
    
    // approach the angle and keep doing the control loop. Preserve sync functionality.
    // Returns the last angle read by the setup.
    float approachAngle(int targetAngle, int wrap=1, int steps = 30);
    
    
  private:
    Servo controlSignal;
  
    int controlPin;     
    int feedbackPin;  
    
    int anglePrecision; // target angular precision for the motor - default set to 5.
    float currentAngle; // current angle of the motor
    int motorSpeed;     // set speed of the motor
    
    // Actuator-specific variables (for Parallax Feedback 360° High-Speed Servo)
    int controlPWMperiod = 20 ;     // delay in ms, before sending another control pulse
    int controlPulseOffset = 1500; // pulse length in us to stop the motor (offset pulse)
    int controlMaxSpeed = 220;     // max speed for the motor
    
    int feedbackMinPeriod = 1000;  // min period of the feedback pwm, in us
    int feedbackMaxPeriod = 1200;  // max period of the feedback pwm, in us
    float feedbackMinDC = 0.029;   // min duty cycle of the feedback pwm (0 deg)
    float feedbackMaxDC = 0.971;   // max duty cycle of the feedback pwm (360 deg)
     
    int cLoopSpeedOffset = 30;     // speed offset for the control loop  
    int rotationPolarity = -1;     // polarity of rotation, either -1 or +1
};

#endif