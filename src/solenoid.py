"""
@file solenoid.py

@brief Contains the SolenoidController class

An instance of Solenoid contains information on and controls a 
single solenoid using the functios outlined below.

@author Zhaodong Zheng
"""

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

class SolenoidController:
    """
    Controls a solenoid through a relay connected to a GPIO
    pin on the Raspberry Pi. The functions in this class
    are essentially just wrappers for setting. This class
    uses threads to make solenoid operations non-blocking
    """

    def __init__(self, pin_num=18):
        self.pin_num = pin_num

        self.on = False

    def solenoid_(self):
