/*
  Arduino program for Eve the Eavesdropper (Chapter 5). 
  Implemented features: see the HELP section
 Author: Qcumber (2018), JH (2022)
 Version: 1.0
*/

#include <EEPROM.h>
#include "EEPROMAnything.h"
//#include <Stepper.h>
#include <PolarizerMotor.h>
#include <Entropy.h>

// Important parameters
const int seqLength = 16;  // Polarisation sequence length (16 bit)
//const int pinLsr = 12;     // Laser pin - not needed for Eve
const int pinDeb = 13;     // Debugging pin (LED on the board)
const int sensorLoc1 = 0;   // A0 - Detector 1
const int sensorLoc2 = 1;  //A1 - Detector 2
int catchTh = 200;   // Threshold in CATCH command 200 = ~1V.

// Parameters
const int stepDelay = 2; // 2 ms
const int stepSpeed = 1000; // 1000 rpm: any number high enough would do
const int stepsPerRevolution = 2048; 

const int serialTimeout = 100; // 100 ms

const int EEloc_angleCurrent1 = 0; // Takes 2 bytes
const int EEloc_angleTarget1 = 2;  // Takes 2 bytes
const int EEloc_angleCurrent2 = 4; // Takes 2 bytes
const int EEloc_angleTarget2 = 6;  // Takes 2 bytes

int polOffset1 = 0; // Polarisation offset, retrieve and store in EEProm
int polOffset2 = 0;
const int EEloc_polOffset1 = 8;  // Takes 2 bytes
const int EEloc_polOffset2 = 10; // Takes 2 bytes

int polSeq[seqLength] = {0}; // int datatype, in multiples of 45 degrees.

const int seqStepTime = 300;  // Time between each steps. Def: 200 ms
const int seqInitTarget = 1;   // Set initialization polarisation for seq always (D)
const int seqPinStart = 0;  // Time in sequence to start / ON the pin
const int seqPinStop = 300;   // Time in sequence to stop / OFF the pin
const int seqReadTime = 150;  // 100 ms (hopefully in the middle of the laser pulse)
const int seqSyncBlink = 300;  // 200 ms (to initialise the signal)
//int moveType;
int moveStepper(int moveType = 1, int motor = 0, int steps = 30); //2:approachAngle, anything else: gotoAngle 

// To deal with floating point rounding off error
// in the conversion between angle and steps,
// we define a variable which keeps track of that.
float stepsErrAcc = 0; 
    
// initialize the two motors (control, feedback): (8,9) and (4,5)
// feedback should be pwm pin indicated by ~ on Arduino

PolarizerMotor myMotor1(8,9);
PolarizerMotor myMotor2(4,5);

void setup() {
  // set the speed at 60 rpm: 
  myMotor1.initialize();
  myMotor2.initialize();
  // myMotor.setSpeed(stepSpeed);
  // initialize the serial port:
  Serial.begin(38400);
  Serial.setTimeout(serialTimeout);
  // Obtain the polarisation offset from EEProm
  EEPROM_readAnything(EEloc_polOffset1, polOffset1);
  EEPROM_readAnything(EEloc_polOffset2, polOffset2);
  // Set the laser pin to be output
  //pinMode(pinLsr, OUTPUT);
  pinMode(pinDeb, OUTPUT); // For debugging
  // Set up the entropy library (to generate random numbers)
  Entropy.initialize();
}

// Main Loop
void loop() {
  while (!Serial.available()); // Listen to serial input
  char serbuf[16] = ""; // Reinitialise buffer (16 bytes, char array size 16)
  Serial.readBytesUntil(' ', serbuf, 15); // Until whitespace
  // Serial.print("serbuf is:"); // Debug
  // Serial.println(serbuf); // Debug
  // Obtain which input command (enumerated)
  int enumc = -1; // default choice
  int maxChoice = 15;
  char sercmd[maxChoice][8] = {"HELP",                //0
    "SETANG1", "ANG1?", "SETPOL1", "POL1?", "VOLTS?", //5
    "SETANG2", "ANG2?", "SETPOL2", "POL2?", "*IDN?",  //10
    "HOF1?", "SETHOF1", "HOF2?", "SETHOF2"};          //14
  for (int c=0; c<maxChoice; c++){
    if (strcasecmp(sercmd[c],serbuf) == 0){ 
      enumc = c;// Obtain match
    }
  }

  // Declaring some other parameters
  char valbuf[16] = "";      // Buffer to receive chartype value from serial
  int angleTarget1;
  int angleTarget2;
  int setPolTo1;
  int setPolTo2;
  float polFloat1;
  float polFloat2;
  char polseqbuf[seqLength] = ""; // Buffer to receive chartype pol sequences from serial 
  int polSeqMod[seqLength] = {0}; // Polarisation sequence within the range (0,3).       
  int sensorValue1;
  int sensorValue2;

  
  
  // Switching between different cases
  switch(enumc){
    
    case 0: //HELP
      Serial.print(F("Quantum Key Construction\n"));
      Serial.print(F("HELP        \t    Print help statement\n"));
      Serial.print(F("SETANG1 X    \t    Set angle to X (in degrees)\n"));
      Serial.print(F("ANG1?        \t    Ask for current angle\n"));
      Serial.print(F("SETPOL1 X    \t    Set polarisation to X -> 0(H), 1(D), 2(V), 3(A)\n"));
      Serial.print(F("POL1?        \t    Ask for current polarisation\n"));
      Serial.print(F("VOLTS?       \t    Ask for sensor voltage\n"));
      Serial.print(F("SETANG2 X    \t    Set angle to X (in degrees)\n"));
      Serial.print(F("ANG2?        \t    Ask for current angle\n"));
      Serial.print(F("SETPOL2 X    \t    Set polarisation to X -> 0(H), 1(D), 2(V), 3(A)\n"));
      Serial.print(F("POL2?        \t    Ask for current polarisation\n"));
      Serial.print(F("VOLT2?       \t   (Deprecated) Ask for sensor voltage\n"));
      Serial.print(F("*IDN?       \t    Gets device name (Quantum/Classical)\n"));
      break; 
      
    case 1: //SETANG1 X
      // listen again (for angle)
      while (!Serial.available());
      Serial.readBytesUntil(' ', valbuf, 15); // Until whitespace
      angleTarget1 = atoi(valbuf);
      EEPROM_writeAnything(EEloc_angleTarget1, angleTarget1);
      moveStepper(1,1); // moveType 1, motor 1
      Serial.println(F("OK"));
      break;
      
    case 2: //ANG1?
      //EEPROM_readAnything(EEloc_angleTarget, angleTarget);
      Serial.println(myMotor1.readAngle());
      break;
      
    case 3: //SETPOL1 X
      // listen again (for polarisation)
      while (!Serial.available());
      Serial.readBytesUntil(' ', valbuf, 15); // Until whitespace
      setPolTo1 = (int)valbuf[0] - 48; // Only convert the first char: the rest are bullshit
      if (setPolTo1 < 0 || setPolTo1 > 3){
        Serial.println("Input error detected.");
        setPolTo1 = 0; // If input error, assume zero polarisation (H)
      }
      angleTarget1 = setPolTo1 * 45 + polOffset1;
      EEPROM_writeAnything(EEloc_angleTarget1, angleTarget1);
      moveStepper(1,1);
      Serial.println("OK");
      break;
      
    case 4: //POL1?
      EEPROM_readAnything(EEloc_angleTarget1, angleTarget1);
      // Convert to polarisation
      polFloat1 = (angleTarget1 - polOffset1) / 45.; 
      Serial.println(polFloat1);
      break;
      
    case 5: //VOLTS?
      sensorValue1 = analogRead(sensorLoc1);
      sensorValue2 = analogRead(sensorLoc2);
      // Serial.print("Val: ");
      Serial.println(sensorValue1);
      Serial.println(sensorValue2);
      break;

    case 6: //SETANG2 X
      // listen again (for angle)
      while (!Serial.available());
      Serial.readBytesUntil(' ', valbuf, 15); // Until whitespace
      angleTarget2 = atoi(valbuf);
      // Serial.print("angleTarget is:"); //Debug
      // Serial.println(angleTarget); // Debug
      EEPROM_writeAnything(EEloc_angleTarget2, angleTarget2);
      moveStepper(1,2);
      Serial.println("OK");
      break;
      
    case 7: //ANG2?
      //EEPROM_readAnything(EEloc_angleTarget, angleTarget);
      Serial.println(myMotor2.readAngle());
      break;
      
    case 8: //SETPOL2 X
      // listen again (for polarisation)
      while (!Serial.available());
      Serial.readBytesUntil(' ', valbuf, 15); // Until whitespace
      setPolTo2 = (int)valbuf[0] - 48; // Only convert the first char: the rest are bullshit
      if (setPolTo2 < 0 || setPolTo2 > 3){
        Serial.println("Input error detected.");
        setPolTo2 = 0; // If input error, assume zero polarisation (H)
      }
      angleTarget2 = setPolTo2 * 45 + polOffset2;
      EEPROM_writeAnything(EEloc_angleTarget2, angleTarget2);
      moveStepper(1,2);
      Serial.println("OK");
      break;
      
    case 9: //POL2?
      EEPROM_readAnything(EEloc_angleTarget2, angleTarget2);
      // Convert to polarisation
      polFloat2 = (angleTarget2 - polOffset2) / 45.; 
      Serial.println(polFloat2);
      break;

    case 10: //*IDN?
      Serial.println("QuantumEve");
      break;

    case 11: //HOF1?
      EEPROM_readAnything(EEloc_polOffset1, polOffset1);
      Serial.println(polOffset1);
      break;

    case 12: //SETHOF1 X
      // listen again (for ofset value)
      while (!Serial.available());
      Serial.readBytesUntil(' ', valbuf, 15); // Until whitespace
      polOffset1 = atoi(valbuf);
      EEPROM_writeAnything(EEloc_polOffset1, polOffset1);
      Serial.println(F("OK"));
      break;

    case 13: //HOF2?
      EEPROM_readAnything(EEloc_polOffset1, polOffset1);
      Serial.println(polOffset1);
      break;

    case 14: //SETHOF2 X
      // listen again (for ofset value)
      while (!Serial.available());
      Serial.readBytesUntil(' ', valbuf, 15); // Until whitespace
      polOffset2 = atoi(valbuf);
      EEPROM_writeAnything(EEloc_polOffset2, polOffset2);
      Serial.println(F("OK"));
      break;
    
    default:
      Serial.println("Unknown command");
      break;
  }
}  

// Helper functions

int specialMod(int num, int mod){
  // Special modulus operation to limit to positive modulus number
  int result = num % mod;
  if (result < 0){
    result += mod;
  }
  return result;
}

int moveStepper(int moveType, int motor, int steps) {
  int current;
  int target;
  if (motor==1) {
    EEPROM_readAnything(EEloc_angleTarget1, target);
    if (moveType==2) {
      myMotor1.approachAngle(target, steps);
    } else {
      myMotor1.gotoAngle(target);
    }
    return 1;
  }
  if (motor==2) {
    EEPROM_readAnything(EEloc_angleTarget2, target);
    if (moveType==2) {
      myMotor2.approachAngle(target, steps);
    } else {
      myMotor2.gotoAngle(target);
    }
    return 1;
  } else {
    // Should not appear since moveStepper is only called internally.
    Serial.println("Motor not detected. Please check pin connections and try again.");
  }
}
