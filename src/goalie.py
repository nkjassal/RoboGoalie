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

  ######## GENERAL PARAMETER SETUP ########
  MOVE_DIST_THRESH = 212 # distance at which robot will stop moving
  SOL_DIST_THRESH = 205 # distance at which solenoid fires
  PACKET_DELAY = 5 # number of frames between sending data packets to pi
  OBJECT_RADIUS = 13 # opencv radius for circle detection
  AXIS_SAFETY_PERCENT = 0.3 # robot stops if within this % dist of axis edges

  packet_cnt = 0
  tracker.radius = OBJECT_RADIUS

  ######## SERVER SETUP ########
  motorcontroller_setup = False
  if server:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # GET SERVER ADDRESS BY GOING TO NETWORK SETTINGS AND CHECKING ETHERNET
    #server_address = ('169.254.242.33',10000)
    #server_address = ('169.254.88.56', 10000)
    server_address = ('localhost', 10000) # for local testing
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
    closest_pt = None
    if closest_obj_index is not None:
      closest_obj = object_list[closest_obj_index]
      closest_pt = points[closest_obj_index]
      # only for viewing, eventually won't need this one (only display traj)
      closest_line = utils.get_line(closest_obj, closest_pt) # only for viewing
      cv2.circle(frame, (int(closest_pt.x),int(closest_pt.y)), 10, colors.Magenta.bgr, -1) # center 

      planner.add_point(closest_obj)


    # Get trajectory - list of elements for bounces, and final line traj
    # Last line intersects with robot axis
    traj_list = planner.get_trajectory_list(colors.Cyan)
    traj = planner.traj


    ######## SOLENOID CODE ########
    # Checks when an object is within a threshold of the robot, then sends
    # the solenoid a signal to push out to hit the ball.



    ######## SEND DATA TO CLIENT ########
    if packet_cnt != PACKET_DELAY:
      packet_cnt = packet_cnt + 1
    else:
      packet_cnt = 0 # reset packet counter

      # error checking to ensure will run properly
      if len(robot_markers) is not 2 or robot is None or closest_pt is None:
        pass
      elif server:
        try:
          if motorcontroller_setup is False:
            # send S packet for motorcontroller setup
            motorcontroller_setup = True


            ######## SETUP MOTORCONTROLLER ########
            axis_pt1 = robot_markers[0].to_pt_string()
            axis_pt2 = robot_markers[1].to_pt_string()
            data = 'SM '+axis_pt1+' '+axis_pt2+' '+robot.to_pt_string()
            print data
            connection.sendall(data)

          # setup is done, send packet with movement data
          # # error checking to ensure runs properly
          # elif closest_pt:
          #   pass
          else:

            obj_robot_dist = utils.get_pt2pt_dist(robot, closest_pt)
            print 'dist: ' + str(obj_robot_dist) # USE FOR CALIBRATION

            # get safety parameters
            rob_ax1_dist = utils.get_pt2pt_dist(robot_markers[0],robot)
            rob_ax2_dist = utils.get_pt2pt_dist(robot_markers[1],robot)
            axis_length = utils.get_pt2pt_dist(robot_markers[0],
              robot_markers[1])

            # ensure within safe bounds of motion relative to axis
            if rob_ax1_dist/axis_length <= AXIS_SAFETY_PERCENT or \
              rob_ax2_dist/axis_length <= AXIS_SAFETY_PERCENT:
              # in danger zone, kill motor movement
              print 'ROBOT OUT OF SAFE REGION: Stopping motor'
              data = 'KM'
              connection.sendall(data)

            # check if solenoid should fire
            elif obj_robot_dist <= SOL_DIST_THRESH: # fire solenoid, dont move
              print 'activate solenoid!'
              pass # TODO SEND SOLENOID ACTIVATE

            # check if robot should stop moving
            elif obj_robot_dist <= MOVE_DIST_THRESH: # obj close to robot
              # Send stop command, obj is close enough to motor to hit
              print 'Stopping motor'
              data = 'KM'
              connection.sendall(data)
              pass 

            # Movement code
            else: # far enough so robot should move

              #### FOR TRAJECTORY ESTIMATION
              # if planner.traj is not None:
              #   axis_intersect=shapes.Point(planner.traj.x2,planner.traj.y2)
              #   # Clamp the point to send to the robot axis
              #   traj_axis_pt = utils.clamp_point_to_line(
              #     axis_intersect, robot_axis)

              #   data = 'D '+robot.to_pt_string()+' '+traj_axis_pt.to_string()
              #   connection.sendall(data)

              #### FOR CLOSEST POINT ON AXIS ####
              if closest_pt is not None and robot is not None:
                data = 'MM ' + robot.to_pt_string() + ' ' + closest_pt.to_string()
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
  robot_color = colors.Green
  rail_color = colors.Yellow
  track_colors = [colors.Black]
  tracker = bt.BallTracker(
    window_name="Robot Goalie Tracking Display",
    robot_color=robot_color,
    robot_marker_color=robot_marker_color,
    rail_color=rail_color,
    track_colors=track_colors, 
    radius=13,
    num_objects = 1) 

  stream(tracker, camera=0, server=0) # begin tracking and object detection



if __name__ == "__main__":
  main()