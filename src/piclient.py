"""
@file piclient.py

Accepts data over ethernet cable from computer, and processes to send the 
motor controller

There are a few data packets that can be sent:

Setup Motor runs setup and intitializes motorcontroller object
SM axis_pt1 axis_pt2 robot_pt
  SM = Setup Motor
  axis_pt1 is a Point object representing one edge of the robot axis
  axis_pt2 is a Point object representing the other edge of the robot axis

Move Motor - sends command to move from robot point to target point
MM robot_pt target_pt
  MM = Move Motor
  robot_pt is a Point object representing the robot's position
  target_pt is a Point object representing the target position to move to

Kill Motor - stops motor movement
KM
  KM = Kill Motor
  No arguments


@author Neil Jassal
"""
import socket
import time

import colors
import shapes
#import motorcontroller2

def main():
  """ 
  @brief Continually polls server for packets, and processes
  """    
  
  # motorcontroller object, initialized once setup gets called
  motorcontroller = None

  # Used to determine if should look to setup the motorcontroller, or if it's
  # already been done, then to poll for data
  setup_done = False

  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Connect the socket to the port where the server is listening
  #server_address = ('169.254.88.56', 10000)
  server_address = ('localhost', 10000) # for local testing
  sock.connect(server_address)

  start_t = time.time()
  while True:
    try:   
      # Receive data
      data = sock.recv(1024)
      data_list = data.split() # splits by ' ' by default

      # Checks to ensure setup has been done or not - this is accounted for
      # on the server side, but check for redundancy

      # only check for S packet, otherwise break
      if setup_done is False:
        if data[:1] == 'SM':

          setup_done = True
          # Parse arguments and send to motorcontroller setup
          # create point objects from axis points and robot
          axis_pt1_list = data_list[1].split(',')
          axis_pt2_list = data_list[2].split(',')
          robot_list = data_list[3].split(',')       

          axis_pt1 = shapes.Point(int(axis_pt1_list[0]),
            int(axis_pt1_list[1]))
          axis_pt2 = shapes.Point(int(axis_pt2_list[0]),
            int(axis_pt2_list[1]))   
          robot_pt = shapes.Point(int(robot_list[0]),
            int(robot_list[1]))
          print 'S '+axis_pt1.to_string() \
            + ' ' + axis_pt2.to_string() + ' ' + robot_pt.to_string()

          # instantiate motorcontroller object UNCOMMENT THIS
          # motorcontroller = Motorcontroller(left_rail_coord=axis_pt1,
          #   right_rail_coord=axis_pt2, robot_coord=robot_pt)
          continue 
        else:
          continue
      
      # setup_done true, check for data

      # check for stop command
      if data[:1] == 'KM':
        print data
        # UNCOMMENT MOTORCONTROLLER COMMAND
        #motorcontroller.stop()

      # check for motor movement command
      if data[:1] == 'MM' and len(data_list) is 3: # MM packet
        # Parse data packet and send to motorcontroller
        robot_pt_list = data_list[1].split(',')
        target_pt_list = data_list[2].split(',')

        robot_pt = shapes.Point(int(robot_pt_list[0]),
          int(robot_pt_list[1]))
        target_pt = shapes.Point(int(float(target_pt_list[0])),
          int(float(target_pt_list[1])))
        print 'D ' + robot_pt.to_string() + ' ' + target_pt.to_string()

        # send motorcontroller command UNCOMMENT THIS
        # motorcontroller.move_to_loc(robot_coord=robot,
          # target_coord=target, style=SINGLE)
      



    except IOError:
      pass

  print 'Closing socket...'
  sock.close()


if __name__ == "__main__":
  main()