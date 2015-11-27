import heapq # for getting max n contours

import numpy as np
import cv2 as cv2
from IPython import embed # for debugging

import colors as color # application-specific constants
import shapes 

class BallTracker:

  def __init__(self, window_name="Ball Tracking",
    scale=0.5, 
    robot_color=color.Red, 
    track_colors=[color.Blue], 
    radius=10, 
    num_per_color = 1,
    debug=0):
    """
    @brief inits default tracking parameters

    @param scale Webcam frame gets scaled by this much (0 to 1).
    @param robot_color The color (from colors.py) of the robot marker
    @param track_colors List of colors (from colors.py) to be tracked. 
    @param radius The min radius circle to be detected
    @param num_per_color The number of objects to detect for one color.
    @param debug enable debug mode
    """

    # if robot marker and track color are the same, won't be able to tell apart
    if robot_color in track_colors:
      print 'Unable to discern robot marker from some objects (same color). Ensure robot marker color is different from colors to be tracked'
      exit()

    self.window_name = window_name
    self.scale = scale

    # The number of frames to average fps over
    self.FPS_FRAMES = 50

    self.num_per_color = num_per_color

    self.robot_color = robot_color
    self.track_colors = track_colors

    self.radius = radius

    self.debug = debug


  def setup_frame(self, frame, scale=0.5, blur_window=11):
    """
    @brief Rescales and blurs frame for clarity and faster operations

    @param frame The frame to be operated on and returned
    @param scale The frame will be scaled multiplicatively by this much (0-1)
    @param blur_window The window size used for the median blur

    @return The updated frame
    @return The updated frame blurred and in hsv
    """  
    # scale is a tuple, not two separate arguments (w, h)
    h_scaled,w_scaled = tuple(self.scale * np.asarray(frame.shape[:2]))
    frame = cv2.resize(frame, (int(w_scaled), int(h_scaled)), 
      cv2.INTER_AREA)
    cv2.flip(src=frame,dst=frame, flipCode=1) # flip across y for correctness

    blur = cv2.GaussianBlur(frame, (blur_window,blur_window), 0) # -0 frames
    img_hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    return frame, img_hsv


  def find_circles(self, img_hsv, colors, num_per_color):
    """
    @brief Finds circle(s) in the frame based on input params, displays 
    on-screen

    Detects circles of the given minimum radius, displays a circle around them 
    and the centroid of each.

    @param img_hsv The frame in HSV to detect circles in
    @param colors The list of colors to be tracked
    @param num_per_color The number of objects of each color to detect

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
      center = None

      # only proceed if at least one contour found
      if len(cnts) > 0:
        # find largest contour in mask, then use it to compute min enclosing
        # circle and centroid
        contours = heapq.nlargest(num_per_color, cnts, 
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

    return circle_list


  def find_robot(self, img_hsv, robot_color):
    """ 
    @brief Finds the robot circle of the specified color

    Only finds one object - expects only one robot in scene

    @param img_hsv The HSV image to find robot in
    @param color The color to detect

    @return robot_pos The tuple of (x,y,radius,center) of the robot
    """
    if robot_color is None:
      return None

    robot_pos = self.find_circles(img_hsv, colors=[robot_color], 
      num_per_color=1)
    if robot_pos == []:
      return None
    else:
      robot_pos[0].color = color.Red # set robot circle display color
      return robot_pos[0]


  def draw_circles(self, img, circle_list):
    """
    @brief Draws circles/centroid from the given circle list onto the frame

    @param img The image to have circles drawn on
    @param circle_list List of tuples containing (x,y,radius)

    @return img The updated image with drawn circles
    """
    for c in circle_list:
      x,y,radius = c.x, c.y, c.radius

      cv2.circle(img, (x,y), radius,
        c.color.bgr, 2)
      cv2.circle(img, (x,y), 5, color.Red.bgr, -1) # center  

    return img
  

  def draw_robot(self, img, robot_pos):
    """
    @brief draws a circle around the robot

    @param frame The frame to draw the circle on
    @param robot_pos A single element list containing the tuple of 
      (x,y,radius,center) of the robot

    @return img The updated image with the robot drawn on
    """
    if robot_pos is None:
      return img
    img = self.draw_circles(img=img, circle_list=[robot_pos])
    return img






