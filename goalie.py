"""
@file goalie.py

@brief Main script for tracking, displaying and moving robot

@author Neil Jassal
"""
import time # for fps counter

import cv2
import numpy as np
from IPython import embed # debugging

import colors # application specific
import shapes
import utils
import tracker as bt
import graphics as gfx
from fps import FPS
from trajectory import TrajectoryPlanner


def stream(tracker, camera=0):
  """ 
  @brief Captures video and runs tracking and moves robot accordingly

  @param tracker The BallTracker object to be used
  @param camera The camera number (0 is default) for getting frame data
    camera=1 is generally the first webcam plugged in
  """
  # create video capture object for
  cap = cv2.VideoCapture(camera)
 # cap = cv2.VideoCapture('media/goalie-test.mov')
  cv2.namedWindow(tracker.window_name)

  # create trajectory planner object
  planner = TrajectoryPlanner(frames=4)

  # create FPS object for frame rate tracking
  fps_timer = FPS()

  while(True):
    # start fps timer
    fps_timer.start_iteration()

    ######## CAPTURE AND PROCESS FRAME ########
    #frame = cv2.imread('media/multi-color.png', 1) # for image testing
    ret, frame = cap.read()
    if ret is False:
      print 'Frame not read'
      exit()

    # resize to 640x480, flip and blur
    frame,img_hsv = tracker.setup_frame(frame=frame, w=640,h=480,
      scale=1, blur_window=15)


    ######## TRACK OBJECTS ########
    # use the HSV image to get Circle objects for robot and objects.
    # object_list is list of Circle objects found.
    # robot is single Circle for the robot position
    # robot_markers is 2-elem list of Circle objects for robot markers
    object_list = tracker.find_circles(img_hsv.copy(), tracker.track_colors,
      tracker.num_objects)
    robot, robot_markers = tracker.find_robot_system(img_hsv)
    rails = tracker.get_rails(img_hsv, robot_markers)

    # Get the line/distances between the robot markers
    # robot_axis is Line object between the robot axis markers
    # points is list of Point objects of closest intersection w/ robot axis
    # distanes is a list of distances of each point to the robot axis
    robot_axis = utils.line_between_circles(robot_markers)
    points, distances = utils.distance_from_line(object_list, robot_axis)


    ######## TRAJECTORY PLANNING ########
    # get closest object and associated point, generate trajectory
    closest_obj_index = utils.min_index(distances) # index of min value
    closest_line = shapes.Line()
    closest_pt = shapes.Point()
    closest_obj = shapes.Circle()
    if closest_obj_index is not None:
      closest_obj = object_list[closest_obj_index]
      closest_pt = points[closest_obj_index]
      # only for viewing, eventually won't need this one (only display traj)
      closest_line = utils.get_line(closest_obj, closest_pt) # only for viewing

      planner.add_point(closest_obj)


    # Get trajectory line between closest object and its' point of intersection
    # on the robot axis
    traj_ln = planner.get_trajectory() # n-frame best fit

    # if trajectory not moving towards robot axis
    if not planner.traj_dir_toward_line(robot_axis):
      traj_ln = None
    traj_int_pt = utils.line_intersect(traj_ln, robot_axis) # Point object
    traj_int_pt = utils.clamp_point_to_line(traj_int_pt, robot_axis)
    traj = utils.get_line(closest_obj, traj_int_pt, color=colors.Cyan)



    ######## ANNOTATE FRAME FOR VISUALIZATION ########
    frame = gfx.draw_robot_axis(img=frame, line=robot_axis) # draw axis line
    frame = gfx.draw_robot(frame, robot) # draw robot
    frame = gfx.draw_robot_markers(frame, robot_markers) # draw markers

    frame = gfx.draw_circles(frame, object_list) # draw objects

    # draw the direct object->axis point (not needed), and trajectory
    # eventually won't need to draw closest line
    frame = gfx.draw_line(img=frame, line=closest_line) # closest obj>axis
    frame = gfx.draw_line(img=frame, line=traj) # draw trajectory estimate



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
  rail_color = colors.Green
  track_colors = [colors.Red]
  tracker = bt.BallTracker(
    window_name="Robot Goalie Tracking Display",
    robot_color=robot_color,
    robot_marker_color=robot_marker_color,
    rail_color=rail_color,
    track_colors=track_colors, 
    radius=13,
    num_objects = 2) 

  stream(tracker, camera=0) # begin tracking and object detection



if __name__ == "__main__":
  main()