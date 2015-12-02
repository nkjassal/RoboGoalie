"""
@file goalie.py

@brief Main script for tracking, displaying and moving robot

@author Neil Jassal
"""
import time # for fps counter

import cv2
import numpy as np
from IPython import embed # debugging

import tracker as bt
import colors
import graphics as gfx
import shapes
import utils
from fps import FPS

DEBUG = False

def stream(tracker, camera=0):
  """ 
  @brief Captures video and runs tracking and moves robot accordingly

  @param tracker The BallTracker object to be used
  @param camera The camera number (0 is default) for getting frame data
  """
  # create video capture object for
  cap = cv2.VideoCapture(camera)
  cv2.namedWindow(tracker.window_name)

  # create FPS object for frame rate tracking
  fps_timer = FPS()

  while(True):
    # start fps timer
    fps_timer.start_iteration()

    ######## CAPTURE AND PROCESS FRAME ########
    frame = None
    if DEBUG:
      frame = cv2.imread('media/complex-2.png',1) # temp for debugging
      if frame is None:
        print 'Failed to read image.'
        exit()
    else:
      ret, frame = cap.read()
      if ret is False:
        print 'Frame not read'
        continue


    if DEBUG:
      frame,img_hsv = tracker.setup_frame(frame=frame,scale=1.0)
    else:
      frame,img_hsv = tracker.setup_frame(frame=frame, scale=0.5,
        blur_window=11)



    ######## TRACK OBJECTS ########
    # use the HSV image to get Circle objects for robot and objects.
    # object_list is list of Circle objects found.
    # robot is single Circle for the robot position
    # robot_markers is 2-elem list of Circle objects for robot markers
    object_list = tracker.find_circles(img_hsv.copy(), tracker.track_colors,
      tracker.num_objects)
    robot, robot_markers = tracker.find_robot_system(img_hsv)

    # Get the line/distances between the robot markers
    # robot_axis is Line object between the robot axis markers
    # points is list of Point objects of closest intersection w/ robot axis
    # distanes is a list of distances of each point to the robot axis
    robot_axis = utils.line_between_circles(robot_markers)
    points, distances = utils.distance_from_line(object_list, robot_axis)

    # Get list of Line objects for each object to its closest axis intersection
    lines = utils.get_lines(object_list, points, colors.Green)



    ######## DRAW ANNOTATIONS ON FRAME ########
    frame = gfx.draw_circles(frame, object_list) # draw objects
    frame = gfx.draw_robot(frame, robot) # draw robot
    frame = gfx.draw_robot_markers(frame, robot_markers) # draw markers
    frame = gfx.draw_robot_axis(img=frame, line=robot_axis) # draw axis line
    frame = gfx.draw_lines(frame=frame, line_list=lines) # draw obj->axis lines

    ######## FPS COUNTER ########
    fps_timer.get_fps()
    fps_timer.display(frame)

    ######## DISPLAY FRAME ON SCREEN ########
    cv2.imshow(tracker.window_name,frame)

    # quit by pressing q
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # release capture
  cap.release()
  cv2.destroyAllWindows()



def main():
  """ 
  @brief Initializes the tracker object and runs goalie script
  """    
  robot_marker_color = colors.Blue
  robot_color = colors.White
  track_colors = [colors.Red]
  tracker = bt.BallTracker(
    window_name="Robot Goalie Object Tracking Display",
    robot_color=robot_color,
    robot_marker_color=robot_marker_color, 
    track_colors=track_colors, 
    radius=13,
    num_objects = 3) 

  stream(tracker, camera=1) # begin tracking and object detection



if __name__ == "__main__":
  main()