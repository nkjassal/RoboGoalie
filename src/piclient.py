"""
@file piclient.py

Accepts data over ethernet cable from computer, and processes to send the 
motor controller

There are two data formats: setup, and data:
Setup format:
S axis_pt1 axis_pt2 robot_pt
  S is the letter S, for denoting the message as setup
  axis_pt1 is a Point object representing one edge of the robot axis
  axis_pt2 is a Point object representing the other edge of the robot axis

Data format:
D robot_pt target_pt
  D is the letter D, denoting the message as data
  robot_pt is a Point object representing the robot's position
  target_pt is a Point object representing the target position to move to


@author Neil Jassal
"""
import socket
import time

import colors
import shapes
#import motorcontroller

def main():
  """ 
  @brief Continually polls server for packets, and processes
  """    
  ### test code
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Connect the socket to the port where the server is listening
  server_address = ('169.254.88.56', 10000)
  sock.connect(server_address)

  start_t = time.time()
  while True:
    try:   
      # Receive data
      data = sock.recv(1024)


    except IOError:
      pass

  print 'closing socket'
  sock.close()

  # Wait for setup data packet before continuing
  # Use setup data packet to create motorcontroller object

  # Continually poll for data, adjusting motor whenever data is received



if __name__ == "__main__":
  main()