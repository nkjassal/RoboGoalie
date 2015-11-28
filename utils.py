"""
@file utils.py

@brief Contains general object conversion functions, math functions, etc.

@author Neil Jassal
"""
import math

import shapes


def get_line_from_circles(robot=None, c1=None, c2=None):
  """
  @brief Gets the Line from two circles, or a robot_pos (list of 2 circles)

  @param robot A list of two circle objects TODO create robot class
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


def get_distance_from_line(circle_list, line):
  """
  @brief Gets the shortest distance from each circle to the given line

  Adapted from: http://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment

  @param circle_list The list of Circles to get distances from line
  @param line The Line object to get distances from

  @return distances A list of distances. distances[i] corresponds to
    circle_list[i]. Returns None if no circles found
  """
  distances = []

  # if no line or no circles return None
  if line is None or not circle_list:
    return None

  for c in circle_list:
    
    line_dot = line.dx*line.dx + line.dx*line.dx
    if float(line_dot) is 0.0: # avoid divide by 0
      distances.append(-1.0)
      continue

    u = ((c.x - line.x1)*line.dx + (c.y - line.y1)*line.dy) / float(line_dot) 
    if u > 1:
      u = 1
    elif u < 0:
      u = 0

    x = line.x1 + u * line.dx
    y = line.y1 + u * line.dy
    dx = x - c.x
    dy = y - c.y

    dist = math.sqrt(dx*dx + dy*dy)

    # ensures nonexistent circles
    if dist <= 0.1:
      distances.append(-1.0)
    else:
      distances.append(dist)

  return distances


