"""
@file solenoid.py

@brief Contains the SolenoidController class

An instance of Solenoid contains information on and controls a
single solenoid using the functios outlined below.

@author Zhaodong Zheng
"""

import RPi.GPIO as GPIO
import time
import threading

class SolenoidController:
    """
    Controls a solenoid through a relay connected to a GPIO
    pin on the Raspberry Pi. The functions in this class
    are essentially just wrappers for setting. This class
    uses threads to make solenoid operations non-blocking
    """

    def __init__(self, pin_num=4):
        """
        @brief Initializes the SolenoidController with the necessary
        information

        @param pin_num The GPIO pin (using BCM) that the solenoid is
        being controlled with
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_num, GPIO.OUT)
        self.pin_num = pin_num
        self.on = False
        self.extend_duration = 0

    def turn_on_worker(self, duration):
        """
        @brief Engages the solenoid (provided it is wired correctly)
        for the duration specified

        @param duration The desired duration for the solenoid to enage,
        in millisecionds
        """
        GPIO.output(self.pin_num, GPIO.HIGH)
        time.sleep(duration * 0.001)
        GPIO.output(self.pin_num, GPIO.LOW)
        #GPIO.cleanup()
        self.on = False

    def turn_on(self, duration):
        """
        @brief Launches the thread to engage the solenoid

        @param duration The desired duration for the solenoid to enage,
        in millisecionds
        """
        #Create the thread controlling the solenoid and run it
        #if another thread is not already running
        solenoid_thread = threading.Thread(target=self.turn_on_worker,
                                args=(duration,))
        self.on = True
        solenoid_thread.start()

    def is_on(self):
        """
        @brief Returns whether or not the solenoid is on
        """
        return self.on

