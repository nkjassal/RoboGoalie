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

import colors
import shapes
import motorcontroller

def main():
  """ 
  @brief Continually polls server for packets, and processes
  """    
  
  # Wait for setup data packet before continuing
  # Use setup data packet to process 



if __name__ == "__main__":
  main()