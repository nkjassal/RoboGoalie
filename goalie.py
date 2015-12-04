"""
@file goalie.py

@brief Main script for tracking, displaying and moving robot

@author Neil Jassal
"""
import time # for fps counter

import cv2
import numpy as np
from IPython import embed # debugging

import colors
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
  #cap = cv2.VideoCapture(camera)
  cap = cv2.VideoCapture('media/goalie-test.mov')
  cv2.namedWindow(tracker.window_name)

  # create trajectory planner object
  planner = TrajectoryPlanner()

  # create FPS object for frame rate tracking
  fps_timer = FPS()

  while(True):
    # start fps timer
    fps_timer.start_iteration()

    ######## CAPTURE AND PROCESS FRAME ########
    ret, frame = cap.read()
    if ret is False:
      print 'Frame not read'
      exit()


    # resize to 640x480 for streaming/video sources
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

    # Get the line/distances between the robot markers
    # robot_axis is Line object between the robot axis markers
    # points is list of Point objects of closest intersection w/ robot axis
    # distanes is a list of distances of each point to the robot axis
    robot_axis = utils.line_between_circles(robot_markers)
    points, distances = utils.distance_from_line(object_list, robot_axis)


    ######## TRAJECTORY PLANNING ########
    # get closest object and associated point, generate line
    closest_obj_index = utils.min_index(distances)
    closest_line = shapes.Line()
    closest_pt = shapes.Point()
    closest_obj = shapes.Circle()
    if closest_obj_index is not None:
      closest_obj = object_list[closest_obj_index]
      closest_pt = points[closest_obj_index]
      closest_line = utils.get_line(object_list[closest_obj_index],
        points[closest_obj_index])
      planner.update_frames(closest_obj)


    # attempt to get point of intersection of trajectory and robot axis
    traj_ln = planner.get_traj() # frame-to-frame line, very small length
    traj_int_pt = utils.line_intersect(traj_ln, robot_axis)

    traj = utils.get_line(closest_obj, traj_int_pt, color=colors.Cyan)
    if traj_int_pt is not None:
      traj_int_pt = utils.clamp_point_to_line(traj_int_pt, robot_axis)




    # gets all lines - not needed, only need to use closest
    # Get list of Line objects for each object to its closest axis intersection
    # lines = utils.get_lines(object_list, points, colors.Green)


    ######## DRAW ANNOTATIONS ON FRAME ########
    frame = gfx.draw_circles(frame, object_list) # draw objects
    frame = gfx.draw_robot(frame, robot) # draw robot
    frame = gfx.draw_robot_markers(frame, robot_markers) # draw markers
    frame = gfx.draw_robot_axis(img=frame, line=robot_axis) # draw axis line
    frame = gfx.draw_line(img=frame, line=closest_line) # closets obj>axis
    #frame = gfx.draw_lines(frame=frame, line_list=lines) # draw obj>axis line
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
  track_colors = [colors.Red]
  tracker = bt.BallTracker(
    window_name="Robot Goalie Tracking Display",
    robot_color=robot_color,
    robot_marker_color=robot_marker_color, 
    track_colors=track_colors, 
    radius=13,
    num_objects = 3) 

  stream(tracker, camera=1) # begin tracking and object detection



if __name__ == "__main__":
  main()