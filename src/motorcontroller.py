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
import utils

class MotorController:
    """
    Note: Class and functions only work for stepper motors. DC motors are not 
    supported.
    Contains information on a single robot and has functions that can be used
    to it. Also contains information on the locations of the rails to prevent
    collisions.
    """

    #Have PID control stuff in here, might not need it
    def __init__(self, HAT_addr=0x60, 
        motor_portnum=1,
        motor_steps=200,
        gear_radius=0.3,
        robot_coord,
        left_rail_coord,
        rght_rail_coord,
        edge_length=0.0,
        KP=1,
        KI=1,
        KD=1,
        KI_error_thresh=0.2,
        error_thresh=0.2
        ):
        """
        @brief Initializes the MotorController with the necessary information

        @param HAT_addr The I2C address of the MotorHAT. Default value is the
        I2C address if only using one MotorHAT
        @param motor_portnum The port number on the HAT of the motor being 
        controlled
        @param motor_steps The steps per rotation of the motor
        @param radius of the gear in cm
        @param robot_coord The location of the robot in a Point object
        @param left_right_coord The coordinate of the left rail, from the 
        perspective of the robot. This is necessary to ensure that the robot 
        does not collide with the left rail (Point object)
        @param rght_rail_coord The coordinate of the right rail, from the 
        perspective of the robot. This is necessary to ensure that the robot 
        does not collide with the right rail (Point object)
        @param edge_length The length of the edge on which the robot traverses
        @param KP The proportional constant for PID control
        @param KI The integral constant for PID control
        @param KD The derivative constant for PID control
        @param KI_error_thresh The error value less than which KI is considered
        zero for PID control
        @param error_thresh The error value less than which the robot is 
        considered to reach its target location

        """
        mh = Adafruit_MotorHAT(addr = HAT_addr)
        self.motor_steps = motor_steps
        self.gear_radius = gear_radius
        #The motor object being controlled
        self.motor = mh.getStepper(motor_steps, motor_portnum)
        self.left_rail_coord = left_rail_coord
        self.rght_rail_coord = rght_rail_coord
        #The distance between the rails in terms of the units used in 
        #the current camera angle
        scaled_edge_length = utils.get_pt2pt_dist(left_rail_coord,
                                                  rght_rail_coord, 0)
        self.edge_length = edge_length
        self.KP=KP
        self.KI=KI
        self.KD=KD
        self.KI=KI_error_thresh = KI_error_thresh
        self.error_thresh = error_thresh
        #The accumulated error for the PID controller
        self.iState = 0.0 
        #The previous position of the robot
        self.dState = robot_coord 
        #Since the motor is being controlled with threads, two threads cannot
        #be controlling the motor at the same time
        self.moving = False 

    def motor_worker(self, numsteps, direction, style='SINGLE'):
        """
        @brief The worker function for the thread that will move the
        stepper motor a certain numer of steps. If no style is given, or
        an invalid style is give, the function will use the single step
        style

        @param numsteps The desired number of steps for the motor to spin
        @param direction The desired direction for the motor to spin
        @param style SINGLE: Standard steps
                     DOUBLE: Two coils on, more power and more strength
                     INTERLEAVE: Mix of single and double
                     MICROSTEP: More precise, gives 8x more steps to motor

        """
        motorstyle = Adafruit_MotorHAT.SINGLE
        if style is 'DOUBLE':
            motorstyle = Adafruit_MotorHAT.DOUBLE
        elif style is 'INTERLEAVE':
            motorstyle = Adafruit_MotorHAT.INTERLEAVE
        elif style is 'MICROSTEP':
            motorstyle = Adafruit_MotorHAT.MICROSTEP

        self.motor.step(numsteps, direction, motorstyle)
        self.moving = False

    def move_to_loc(self, robot_coord, target_coord, style, reverse_dir=0):
        """
        @brief Moves the robot to a target coordinate by calling the 
        motor_worker function

        @param robot_loc The current location of the robot in a Point object
        @param target_loc The desired location for the robot in a Point object
        @param style SINGLE: Standard steps
                     DOUBLE: Two coils on, more power and more strength
                     INTERLEAVE: Mix of single and double
                     MICROSTEP: More precise, gives 8x more steps to motor
        @param reverse_dir Whether or not to reverse the direction of the
        motor, perhaps because of a change in mounting orientation

        """












        

