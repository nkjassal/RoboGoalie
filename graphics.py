"""
@file graphics.py

Contains drawing and screen annotation functions

@author Neil Jassal
"""

import cv2
import colors
import shapes


def draw_line(img, line):
  """
  @brief Draws a single Line object to the given image

  @param img The image to annotate
  @param line The Line object to draw

  @return img The annotated image
  """
  cv2.line(img, 
    (int(line.x1),int(line.y1)), 
    (int(line.x2),int(line.y2)), 
    color=line.color.bgr, thickness=line.thickness)
  return img

def draw_lines(frame, line_list):
  """
  @brief Draws each line from line_list onto the frame

  @param frame The frame to be updated with lines 
  @param line_list The list of Line objects to be drawn onto frame

  @return frame The updated frame
  """
  for line in line_list:
    frame = draw_line(frame, line)
    # frame = cv2.line(frame, (int(line.x1),int(line.y1)), 
    #   (int(line.x2),int(line.y2)), 
    #   color=line.color.bgr, thickness=line.thickness)
  return frame


def draw_circle(img, c):
  """
  @brief Draws a single Circle object to the given image

  @param img The image to annotate
  @param c The Circle object to draw

  @return img The annotated image
  """
  x,y,radius = c.x, c.y, c.radius

  cv2.circle(img, (x,y), radius, c.color.bgr, 2)
  cv2.circle(img, (x,y), 5, colors.Red.bgr, -1) # center 
  return img

def draw_circles(img, circle_list):
  """
  @brief Draws circles/centroid from the given circle list onto the frame

  @param img The image to have circles drawn on
  @param circle_list List of tuples containing (x,y,radius)

  @return img The updated image with drawn circles
  """
  for c in circle_list:
    draw_circle(img, c) 
  return img


def draw_robot(img, robot):
  """
  @brief draws a circle around the robot

  @param img The image to draw the robot on
  @param robot The circle object representing the robot

  @return img The annotated image
  """
  if robot is None:
    return img
  img = draw_circle(img=img, c=robot)
  return img

def draw_robot_markers(img, robot_pos):
  """
  @brief draws a circle around the robot markers

  @param img The frame to draw the circle on
  @param robot_pos A list containing Circle objects for the two robot markers

  @return img The updated image with the robot drawn on
  """
  if robot_pos is []:
    return img
  img = draw_circles(img=img, circle_list=robot_pos)
  return img


def draw_robot_axis(img, robot_pos=None, line=None):
  """
  @brief Draws a line between the robot markers, denoting the axis of motion

  Only one of robot_pos or line needs to be supplied.
  
  If a line is supplied, it will draw using the line. Otherwise, if the
  robot marker positions are supplied, it will calculate the line and
  display using that. If neither parameter is given, no line will be 
  displayed

  @param img The frame to draw the line on
  @param robot_pos A list containing Circle objects for the two robot markers
  @param line A line object from shapes.py. Can be supplied if the Line
    object already exists, otherwise will be calculated from robot_pos, if
    it exists

  @return img The updated image with the robot drawn on
  """
  if line is not None:
    img = cv2.line(img, (line.x1,line.y1), (line.x2,line.y2),
      color=line.color.bgr, thickness=line.thickness)

  # No line object given, draw line using robot_pos
  elif robot_pos is not None:
    img = cv2.line(img, 
      (robot_pos[0].x, robot_pos[0].y),
      (robot_pos[1].x, robot_pos[1].y),
      color=colors.Red.bgr, thickness=3)  

  return img