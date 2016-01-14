"""
@file goalie.py

@brief Main script for tracking, displaying and moving robot

@author Neil Jassal
"""
import time # for fps counter

import cv2
import numpy as np
from IPython import embed # debugging
import socket

import colors # application specific
import shapes
import utils
import tracker as bt
import graphics as gfx
from fps import FPS
from trajectory import TrajectoryPlanner
from videostream import WebcamVideoStream


def stream(tracker, camera=0, server=0):
  """ 
  @brief Captures video and runs tracking and moves robot accordingly

  @param tracker The BallTracker object to be used
  @param camera The camera number (0 is default) for getting frame data
    camera=1 is generally the first webcam plugged in
  """

  ######## SERVER SETUP ########
  motorcontroller_setup = False
  if server:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # GET SERVER ADDRESS BY GOING TO NETWORK SETTINGS AND CHECKING ETHERNET
    #server_address = ('169.254.242.33',10000)
    #server_address = ('169.254.88.56', 10000)
    #server_address = ('localhost', 10000) # for local testing
    print 'starting up on %s port %s' % server_address
    sock.bind(server_address)
    sock.listen(1)
    connection, client_address = None, None
    while True:
      # Wait for a connection
      print 'waiting for a connection'
      connection, client_address = sock.accept()
      break


  ######## CV SETUP ########

  # create video capture object for
  #cap = cv2.VideoCapture(camera)
  #cap = WebcamVideoStream(camera).start() # WEBCAM

  #cap = cv2.VideoCapture('../media/goalie-test.mov')
  cap = cv2.VideoCapture('../media/bounce.mp4')

  cv2.namedWindow(tracker.window_name)

  # create trajectory planner object
  # value of bounce determines # of bounces. 0 is default (no bounces)
  planner = TrajectoryPlanner(frames=4, bounce=0)

  # create FPS object for frame rate tracking
  fps_timer = FPS(num_frames=20)


  while(True):
    # start fps timer
    fps_timer.start_iteration()

    ######## CAPTURE AND PROCESS FRAME ########
    #frame = cv2.imread('../media/rails-1.png', 1) # for image testing
    #ret, frame = True, cap.read() # WEBCAM
    ret, frame = cap.read() # for non-webcam
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
    walls = tracker.get_rails(img_hsv, robot_markers, colors.Yellow)
    planner.walls = walls

    # Get the line/distances between the robot markers
    # robot_axis is Line object between the robot axis markers
    # points is list of Point objects of closest intersection w/ robot axis
    # distanes is a list of distances of each point to the robot axis
    robot_axis = utils.line_between_circles(robot_markers)
    points, distances = utils.distance_from_line(object_list, robot_axis)
    planner.robot_axis = robot_axis

    ######## TRAJECTORY PLANNING ########
    # get closest object and associated point, generate trajectory
    closest_obj_index = utils.min_index(distances) # index of min value
    closest_line = None
    if closest_obj_index is not None:
      closest_obj = object_list[closest_obj_index]
      closest_pt = points[closest_obj_index]
      # only for viewing, eventually won't need this one (only display traj)
      closest_line = utils.get_line(closest_obj, closest_pt) # only for viewing

      planner.add_point(closest_obj)


    # Get trajectory - list of elements for bounces, and final line traj
    # Last line intersects with robot axis
    traj_list = planner.get_trajectory_list(colors.Cyan)
    traj = planner.traj


    ######## SOLENOID CODE ########
    # Checks when an object is within a threshold of the robot, then sends
    # the solenoid a signal to push out to hit the ball.



    ######## SEND DATA TO CLIENT ########
    if server:
      try:
        if motorcontroller_setup is False:
          # send S packet for motorcontroller setup
          motorcontroller_setup = True


          ######## SETUP MOTORCONTROLLER ########
          axis_pt1 = robot_markers[0].to_pt_string()
          axis_pt2 = robot_markers[1].to_pt_string()
          data = 'S '+axis_pt1+' '+axis_pt2+' '+robot.to_pt_string()
          print data
          connection.sendall(data)

        # setup is done, send D packet with movement data
        else:


          ######## MOTOR CONTROL ########
          # First clamp final trajectory intersection to robot axis

          #### FOR TRAJECTORY ESTIMATION
          # if planner.traj is not None:
          #   axis_intersect = shapes.Point(planner.traj.x2, planner.traj.y2)
          #   # Clamp the point to send to the robot axis
          #   traj_axis_pt = utils.clamp_point_to_line(
          #     axis_intersect, robot_axis)

          #   data = 'D ' + robot.to_pt_string() + ' ' + traj_axis_pt.to_string()
          #   connection.sendall(data)

          #### FOR CLOSEST POINT ON AXIS
          if closest_pt is not None and robot is not None:
            data = 'D ' + robot.to_pt_string() + ' ' + closest_pt.to_string()
            print data
            connection.sendall(data)

      except IOError:
        pass # don't send anything



    ######## ANNOTATE FRAME FOR VISUALIZATION ########
    frame = gfx.draw_lines(img=frame, line_list=walls)

    frame = gfx.draw_robot_axis(img=frame, line=robot_axis) # draw axis line
    frame = gfx.draw_robot(frame, robot) # draw robot
    frame = gfx.draw_robot_markers(frame, robot_markers) # draw markers

    frame = gfx.draw_circles(frame, object_list) # draw objects

    # eventually won't need to print this one
    frame = gfx.draw_line(img=frame, line=closest_line) # closest obj>axis

    # draw full set of trajectories, including bounces
    frame = gfx.draw_lines(img=frame, line_list=traj_list)
    #frame = gfx.draw_line(img=frame, line=traj) # for no bounces
    #frame=gfx.draw_line(frame,planner.debug_line) # for debug



    ######## FPS COUNTER ########
    fps_timer.get_fps()
    fps_timer.display(frame)


    ######## DISPLAY FRAME ON SCREEN ########
    cv2.imshow(tracker.window_name,frame)
    # quit by pressing q
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # release capture
  #cap.stop() # WEBCAM
  cap.release() # for testing w/o webcam
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
    num_objects = 1) 

  stream(tracker, camera=0, server=1) # begin tracking and object detection



if __name__ == "__main__":
  main()