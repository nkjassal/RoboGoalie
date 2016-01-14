"""
@file Shapes.py

@brief Contains classes for shapes, used for location and display

Currently contains classes for:
  Point
  Circle
  Line

@author Neil Jassal
"""
import math

import colors


class Point:    
  def __init__(self, x=0, y=0, color=colors.Red):
    """
    @brief Sets up initial parameters

    @param x The x-coordinate of the point
    @param y The y-coordinate of the point
    """
    self.x = x
    self.y = y
    self.color = color

  def to_string(self):
    """
    @brief Gets a string of the form X,Y
    @return A string of the form 'X,Y', X and Y being the coordinate value
    """
    return str(self.x) + ',' + str(self.y)

class Circle:
  def __init__(self, x=0, y=0, radius=0, centroid=(0,0), color=colors.Green):
    """
    @brief Sets up initial parameters

    @param x The x coordinate of the circle center. From finding minimum 
      enclosing circle.
    @param y the y coordinate of the circle center. From finding minimum
      enclosing circle.
    @param radius The radius of the circle
    @param center A tuple of (x,y) coordinates of the centroid. Comes from 
      calcuation of centroid using moments.
    @param color The display color for the circle
    """
    self.x = x
    self.y = y
    self.coord = (x,y)
    self.radius = radius
    self.centroid = centroid
    self.color = color

  def to_pt_string(self):
    """
    @brief Gets string of the x,y coords of the circle
    @return String of 'X,Y' format - same as Point to_string() format
    """
    return str(self.x) + ',' + str(self.y)
    
  def to_string(self):
    """
    @brief Gets string of the form X,Y,radius
    @return String of form 'X,Y,R', X and Y being coordinates of the center
      and R being the radius
    """
    return str(self.x) + ',' + str(self.y) + ',' + str(self.radius)


class Line:
  def __init__(self, x1=0, y1=0, x2=0, y2=0, length=0, color=colors.Red,
    thickness=3):
    """
    @brief Sets up initial parameters

    @param x1 x-coordinate of first point
    @param y1 y-coordinate of first point
    @param x2 x-coordinate of second point
    @param y2 y-coordinate of second point
    @param dx The x-distance between points
    @param dy The y-distance between points
    @param length The length of the line. Calculated by default
    @param color The color to be used to display the line
    @param thickness The thickness of the line when drawn
    """
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
    self.dx = (x2 - x1) * 1.0
    self.dy = (y2 - y1) * 1.0

    # for y = mx + b form, m is slope, b is y-intercept
    self.m = None # ensure initialization
    if math.fabs(self.dx) < 0.0001: # vertical line
        self.m = 99999
    else:
        self.m = self.dy / self.dx
    self.slope = self.m
    
    self.b = y1 - self.m * x1

    # display parameters
    self.color = color
    self.thickness = thickness
    
    # Only calculate length if not already provided
    if length is 0:
      self.length = math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2, 2))



