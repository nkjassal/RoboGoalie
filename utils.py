"""
@file utils.py

@brief Contains general object conversion functions, math functions, etc.

@author Neil Jassal
"""
import math

import cv2
from IPython import embed

import shapes
import colors


def clamp(val, min_val, max_val):
  """
  @brief clamps the given value to a specified range

  @param val The value to be clamped
  @param min_val The min value of the range to clamp to
  @param max_val The max value of the range to clamp to

  @return val The new value, clamped in range [min_val, max_val]
  """
  return max(min_val, min(val, max_val))


def get_line(object, point, color=colors.Green):
  """
  @brief Creates Line from object to point

  @param object The Circle object used as one endpoint
  @param point The Point object used as the other endpoint

  @return ln The Line object between object and point
  """
  if point is None:
    return None
  ln = shapes.Line(x1=int(object.x), y1=int(object.y), 
    x2=point.x, y2=point.y, color=color)  
  return ln


def get_lines(object_list, points, color=colors.Green):
  """
  @brief Gets a Line object for each object to the specified point

  Used to get the line between each object and its' single-frame estimated
    final position on the robot axis

  @param object_list The list of objects to use 
  @param points The list of endpoints to generate lines from

  @return lines A list of Line objects for each object in object_list
  """
  lines = []
  if len(object_list) is len(points):
    for i in range(len(object_list)):
      lines.append(get_line(object_list[i], points[i]))
  return lines


def line_between_circles(robot=None, c1=None, c2=None):
  """
  @brief Gets the Line from two circles or the robot markers

  @param robot A list of two circle objects representing robot markers. TODO create robot class
  @param c1 One circle to calculate the Line from. Only used if robot not given
  @param c2 Other circle to get Line from. Only used if robot not given

  @return Line object for the line between both circles
  """
  line = None
  # if no robot, use c1 and c2
  if robot is None:
    line = shapes.Line(
        x1=c1[0].x, y1=c1[0].y,
        x2=c2[1].x, y2=c2[1].y)

  # ensure robot can be used to generate line
  elif len(robot) is 2:
    line = shapes.Line(
          x1=robot[0].x, y1=robot[0].y,
          x2=robot[1].x, y2=robot[1].y) 
  return line


def distance_from_line(circle_list, line):
  """
  @brief Gets the shortest distance from each circle to a given line

  Adapted from: http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment

  Invalid points will have distance of -1, points tuple = None

  @param circle_list The list of Circles to get distances from line
  @param line The Line object to get distances from

  @return points A list of (x,y) tuples corresponding to closest point on line
    to circle i. points[i] corresponds to circle_list[i]
  @return distances A list of distances. distances[i] corresponds to
    circle_list[i]. Returns None if no circles found
  """
  distances = []
  points = []

  # if no line or no circles return None
  if line is None or not circle_list:
    return points, distances

  for c in circle_list:

    line_dot = line.dx*line.dx + line.dy*line.dy
    if float(line_dot) <= 0.00001: # avoid divide by 0
      distances.append(-1)
      points.append(None)
      continue

    px = c.x - line.x1
    py = c.y - line.y1
    
    proj = px*line.dx + py*line.dy
    u = proj / float(line_dot)

    # bounds checking - need to fix to account for negative
    if u > 1.0:
      u = 1.0
    elif u < -1.0: # THIS MAY NEED FIXING
      u = -1.0

    x = line.x1 + u * line.dx
    y = line.y1 + u * line.dy

    # Clamp x and y so the line is never out of range of the robot segment
    x = clamp(x, min(line.x1, line.x2), max(line.x1, line.x2))
    y = clamp(y, min(line.y1, line.y2), max(line.y1, line.y2))

    dx = x - c.x
    dy = y - c.y
    dist = math.sqrt(dx*dx + dy*dy)

    # ensures nonexistent circles have distance of -1, not 0
    if dist <= 0.00001:
      distances.append(-1)
      points.append(None)
    else:
      distances.append(dist)
      points.append( shapes.Point(x,y) )

  return points, distances


