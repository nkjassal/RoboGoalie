"""
@file utils.py

@brief Contains general object conversion functions, math functions, etc.

@author Neil Jassal
"""
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