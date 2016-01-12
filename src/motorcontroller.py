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
        left_rail_coord,
        rght_rail_coord,
        edge_length=0.0,
        KP=1,
        KI=1,
        KD=1,
        robot_coord,
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
        @param left_right_coord The coordinate of the left rail, from the 
        perspective of the robot. This is necessary to ensure that the robot 
        does not collide with the left rail (Point object)
        @param rght_rail_coord The coordinate of the right rail, from the 
        perspective of the robot. This is necessary to ensure that the robot 
        does not collide with the right rail (Point object)
        @param edge_length The length of the edge on which the robot traverses
        in cm
        @param KP The proportional constant for PID control
        @param KI The integral constant for PID control
        @param KD The derivative constant for PID control
        @param robot_coord The location of the robot in a Point object
        @param KI_error_thresh The error value less than which KI is considered
        zero for PID control
        @param error_thresh The error value less than which the robot is 
        considered to reach its target location

        """
        mh = Adafruit_MotorHAT(addr = HAT_addr)
        self.motor_steps = motor_steps
        self.gear_radius = gear_radius
        self.gear_circum = 2.0*3.14159265*gear_radius
        #The motor object being controlled
        self.motor = mh.getStepper(motor_steps, motor_portnum)
        self.left_rail_coord = left_rail_coord
        self.rght_rail_coord = rght_rail_coord
        #The distance between the rails in terms of the units used in 
        #the current camera angle
        self.scaled_edge_length = utils.get_pt2pt_dist(left_rail_coord,
                                                  rght_rail_coord, 0)
        self.edge_length = edge_length
        self.scaled_ovr_real = self.scaled_edge_length/self.edge_length

        #PID control stuff, might not need at all
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
        motor_worker function. Returns the thread running motor_worker so 
        the calling function can check if the motor is still moving with
        the 'moving' field

        @param robot_loc The current location of the robot in a Point object
        @param target_loc The desired location for the robot in a Point object
        @param style SINGLE: Standard steps
                     DOUBLE: Two coils on, more power and more strength
                     INTERLEAVE: Mix of single and double
                     MICROSTEP: More precise, gives 8x more steps to motor
        @param reverse_dir Whether or not to reverse the direction of the
        motor, perhaps because of a change in mounting orientation

        """

        if self.moving = True:
            print "Cannot move motor when motor is already moving"
            return

        #Distances of the robot from the left or right rails, respectively
        dist_to_left = utils.get_pt2pt_dist(robot_coord, self.left_rail_coord)
        dist_to_rght = utils.get_pt2pt_dist(robot_coord, self.rght_rail_coord)
        dist_to_trgt = utils.get_pt2pt_dist(robot_coord, target_coord)
        #Real distance to target in cm
        real_dist_to_trgt = dist_to_trgt/self.scaled_ovr_real

        #Compute direction in which the robot needs to move
        #Point object is used as a vector in this case to use utils.dot
        #Vector from robot to left rail
        robot_to_left = Point(self.left_rail_coord.x-self.robot_coord.x,
                              self.left_rail_coord.y-self.robot_coord.y)
        # #Vector from robot to right rail, probably don't need
        # robot_to_rght = Point(self.rght_rail_coord.x-self.robot_coord.x,
        #                       self.rght_rail_coord.y-self.robot_coord.y)
        #Vector from robot to target
        robot_to_trgt = Point(target_coord.x-self.robot_coord.x,
                              target_coord.y-self.robot_coord.y)
        #Use dot product to find if the direction is towards left or right
        #Direction: -1->left, 1->right
        direction = -1
        if utils.dot(robot_to_left, robot_to_trgt) < 0:
            direction = 1
        if reverse_dir is 1:
            direction = direction * -1
        motor_dir = Adafruit_MotorHAT.FORWARD
        if direction is 1:
            motor_dir = Adafruit_MotorHAT.BACKWARD

        #Compute how many steps the motor should move
        steps = (real_dist_to_trgt/gear_circum)*self.motor_steps
        if style = "MICROSTEP":
            steps = steps * 8

        #Create the thread controlling the motor and run it
        motor_thread = threading.Thread(target=motor_worker, 
                                args=(self.motor, steps, motor_dir, style))
        self.moving = True
        motor_thread.start()

    def is_moving(self):
        """
        @brief Returns whether or not the motor is currently in motion

        """
        return self.moving
