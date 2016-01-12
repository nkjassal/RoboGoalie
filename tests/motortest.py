#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperM$
 
import time
import atexit

mh = Adafruit_MotorHAT(addr = 0x60)
myStepper = mh.getStepper(200, 1)
myStepper.setSpeed(30)