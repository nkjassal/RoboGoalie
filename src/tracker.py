"""
@file tracker.py

@brief Contains the BallTracker class.

The BallTracker class has functions for tracking and displaying circles for 
a given frame. Cirles can be tracked, as well as the 'robot.' The robot isd
denoted as a set of two circles with an axis between them.

@author Neil Jassal
"""

import heapq # built-in packages

import numpy as np # 3rd party packages
import cv2 as cv2
from IPython import embed

import colors # application-specific
import shapes 
import utils

class BallTracker:
  """ 
  Used to track a given number of circular objects with respect to a robot
  system. The system is assumed to be as follows, with each type of object or
  system component having a unique color.

  1 - uniquely colored circle representing the robot (R)
  2 - circles on the bounds of the robot's axis of motion. The robot can only
    move between these two circles. These are robot markers (M)
  2 - circles representing the opposite ends of the rails. Balls can bounce off
    the rails, and the rails will be specified as two lines (on either side of
    the system) from the robot markers. (L)
  3 - circles representing the objects to track. Trackable objects can be of
    multiple colors, but this list of colors must be specified (O)

  Using the convention of robot (R), markers (M), rails (L) and objects (O),
    a sample setup could be approximated below. The '|' symbols represent the
    rails over which the objects can bounce off of

    M     R         M
    |               |
    |   O           |
    |               |
    |           O   |
    |               |
    L               L

  """
  def __init__(self, window_name="Ball Tracking",
    scale=0.5, 
    robot_color=colors.White,
    robot_marker_color=colors.Red, 
    rail_color=colors.Green,
    track_colors=[colors.Blue], 
    radius=10, 
    num_objects = 1,
    debug=0):
    """
    @brief inits default tracking parameters

    @param scale Webcam frame gets scaled by this much (0 to 1).
    @param robot_color The color (from colors.py) of the robot itself
    @param robot_marker_color The color of the axis ends of the robot
    @param rail_color The color of the opposite endpoints of the rail
    @param track_colors List of colors (from colors.py) to be tracked. 
    @param radius The min radius circle to be detected
    @param num_objects The number of objects to detect.
    @param debug enable debug mode
    """
    
    # if robot marker and track color are the same, won't be able to tell apart
    if robot_marker_color in track_colors or robot_color in track_colors:
      print 'Some markers are the same color. Ensure robot, markers, rails and objects all have unique colors'
      exit()

    self.window_name = window_name
    self.scale = scale

    self.num_objects = num_objects

    self.robot_color = robot_color
    self.robot_marker_color = robot_marker_color
    self.rail_color = rail_color
    self.track_colors = track_colors

    self.radius = radius

    self.debug = debug


  def setup_frame(self, frame, w=None, h=None, scale=0.5, blur_window=11):
    """
    @brief Rescales and blurs frame for clarity and faster operations

    @param frame The frame to be operated on and returned
    @param w Value in pixels for scaled frame width
    @param h Value in pixels for scaled height width
    @param scale The frame will be scaled multiplicatively by this much (0-1)
    @param blur_window The window size used for the median blur

    The scale parameter is only used if w or h are not supplied. If w and h
    are supplied, the frame will be resized to the specific size wxh

    @return The updated frame
    @return The updated frame blurred and in hsv
    """ 
    if w is not None and h is not None: # use specified (w,h)
      frame = cv2.resize(frame, (w,h), cv2.INTER_NEAREST)
    else: # use default/specified scale
      # scale argument is a tuple, not two separate arguments (w, h)
      h_scaled,w_scaled = tuple(scale * np.asarray(frame.shape[:2]))
      frame = cv2.resize(frame, (int(w_scaled), int(h_scaled)), 
        cv2.INTER_NEAREST)
    #cv2.flip(src=frame,dst=frame, flipCode=1) # flip over y for visual clarity

    blur = cv2.GaussianBlur(frame, (blur_window,blur_window), 0) # -0 frames
    img_hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    return frame, img_hsv


  ################ OBJECT DETECTION FUNCTIONS ######################
  def find_circles(self, img_hsv, colors, 
    num_objects):
    """
    @brief Finds circle(s) in the frame based on input params, displays 
    on-screen

    Detects circles of the given minimum radius, displays a circle around them 
    and the centroid of each.

    @param img_hsv The frame in HSV to detect circles in
    @param colors The list of colors to be tracked
    @param num_objects The number of objects to detect

    @return circle_list List of detected circles (x,y,radius,center)
    """
    circle_list = []

    # if no colors specified, return empty
    if colors == []:
      return circle_list

    for color in colors:
      # Mask with range of HSV values, uses both color bounds and combines.
      # Erode and dilate to reduce noise
      mask = cv2.bitwise_or(
        cv2.inRange(img_hsv, color.lower0, color.upper0),
        cv2.inRange(img_hsv, color.lower1, color.upper1))
      mask = cv2.erode(mask, None, iterations=2)
      mask = cv2.dilate(mask, None, iterations=2)

      # destructive, so copy mask if needed later
      cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]

      # only proceed if at least one contour found
      if len(cnts) > 0:
        # find largest N contours in mask, then use it to compute min enclosing
        # circle and centroid
        contours = heapq.nlargest(num_objects, cnts, 
          key=cv2.contourArea)
        for c in contours:
          ((x,y), radius) = cv2.minEnclosingCircle(c)
          # only proceed if radius meets certain size
          if radius > self.radius:
            M = cv2.moments(c)
            # if divide by 0 will occur, skip circle
            if int(M["m00"]) is not 0:
              centroid = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
              circle = shapes.Circle(x=int(x), y=int(y), 
                radius=int(radius), centroid=centroid)
              circle_list.append(circle)

    # get the n largest circles, n being num_objects
    circle_list = heapq.nlargest(num_objects, circle_list,
      key=lambda s: s.radius)

    return circle_list


  def find_robot(self, img_hsv):
    """
    @brief Finds the circle representing the robot itself

    @param img_hsv The HSV image to find the robot in

    @return A single circle object representing the robot position
    """
    if self.robot_color is None:
      return []

    robot_pos = self.find_circles(img_hsv, colors=[self.robot_color], 
      num_objects=1)

    if len(robot_pos) < 1:
      return None
    robot_pos[0].color = colors.Magenta # display robot circle as cyan
    return robot_pos[0]   

  def find_robot_markers(self, img_hsv):
    """ 
    @brief Finds the robot axis markers of the specified color

    Only finds two objects. Robot has 1 axis of motion, so distinct circles 
    represent the axis. Expects 2 objects

    @param img_hsv The HSV image to find robot in
    @param color The color to detect

    @return robot_pos A list of the two circle objects for a robot
    """
    if self.robot_marker_color is None:
      return []

    # Find two circles for the axis markers
    robot_pos = self.find_circles(img_hsv, colors=[self.robot_marker_color], 
      num_objects=2)
    if len(robot_pos) < 2:
      return []
    else:
      robot_pos[0].color = colors.Red # set robot circle display color
      robot_pos[1].color = colors.Red
      return robot_pos

  def find_robot_system(self, img_hsv):
    """
    @brief Finds the robot and the robot markers

    Wrapper for find_robot_markers and find_robot

    @param img_hsv The HSV image to find robot in

    @return robot The Circle object representing the robot
    @return robot_axis 2-elem list of Circle objects for the robot axis markers
    """
    robot = self.find_robot(img_hsv.copy())
    robot_axis = self.find_robot_markers(img_hsv.copy())
    return robot, robot_axis


  def get_rails(self, img_hsv, robot_markers, color=colors.Red):
    """
    @brief Gets the 2 lines representing the rails of the system

    Finds 2 objects of rail_color, then creates two lines. Each line goes from
    one robot marker to the closest rail object found. 

    @param img_hsv The HSV image to find robot
    @param robot_markers A 2-elem list of Circles representing robot markers
    @param color The line color of the rail

    @return A 2-element list of Line objects representing the rails. If either
    rail is not found, return empty list
    """
    if len(robot_markers) is not 2:
      return []

    rails = self.find_circles(img_hsv, colors=[self.rail_color], num_objects=2)
    if len(rails) is not 2:
      return []

    # Determine which marker one rail is closer to, generate appropriate lines
    r0_m0_dist = utils.get_pt2pt_dist(rails[0], robot_markers[0], squared=1)
    r0_m1_dist = utils.get_pt2pt_dist(rails[0], robot_markers[1], squared=1)

    # Use rails[0] and markers[0], and rails[1] and markers[1] if true
    if r0_m0_dist < r0_m1_dist:
      ln1 = utils.line_between_circles(c1=rails[0], c2=robot_markers[0])
      ln2 = utils.line_between_circles(c1=rails[1], c2=robot_markers[1])
    else:
      # use rails[0], markers[1], and rails[1], markers[0] as lines
      ln1 = utils.line_between_circles(c1=rails[0], c2=robot_markers[1])
      ln2 = utils.line_between_circles(c1=rails[1], c2=robot_markers[0])     

    ln1.color = color
    ln2.color = color
    return [ln1, ln2]


