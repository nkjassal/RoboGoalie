"""
@file motorcontroller.py

@brief Contains the MotorController class

An instance of Motorcontroller contains information on and controls a 
single motor using the functios outlined below.

@author Zhaodong Zheng
"""

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperM$
 
import time
import atexit

class MotorController:
    """
    Note: Class and functions only work for stepper motors. DC motors are not 
    supported.
    Contains information on a single robot and has functions that can be used
    to it. Also contains information on the locations of the rails to prevent
    collisions.
    """
    def __init__(self, HAT_addr=0x60, 
        motor_portnum=1,
        motor_steps=200,
        left_rail_coord=(0.0, 0.0),
        rght_rail_coord=(0.0, 0.0),
        KP=1,
        KI=1,
        KD=1
        ):
        """
        @brief Initializes the MotorController with the necessary information

        @param HAT_addr The I2C address of the MotorHAT. Default value is the
        I2C address if only using one MotorHAT
        @param motor_portnum The port number on the HAT of the motor being 
        controlled
        @param motor_steps The steps per rotation of the motor
        @param left_right_coord The coordinate of the left rail, from the 
        perspective of the robot. This is necessary to ensure that the robot 
        does not collide with the left rail
        @param rght_rail_coord The coordinate of the right rail, from the 
        perspective of the robot. This is necessary to ensure that the robot 
        does not collide with the right rail
        @param KP The proportional constant for PID control
        @param KI The integral constant for PID control
        @param KD The derivative constant for PID control
        """
        mh = Adafruit_MotorHAT(addr = HAT_addr)
        self.motor = mh.getStepper(motor_steps, motor_portnum)
        self.left_rail_coord = left_rail_coord
        self.rght_rail_coord = rght_rail_coord
        self.KP=KP
        self.KI=KI
        self.KD=KD


