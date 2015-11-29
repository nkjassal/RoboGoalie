"""
@file Shapes.py

@brief Contains classes for shapes, used for location and display

Currently contains classes for:
  Circle
  Line

@author Neil Jassal
"""
import math

import colors as color


class Point:
  def __init__(self, x=0, y=0, color=color.Red):
    """
    @brief Sets up initial parameters

    @param x The x-coordinate of the point
    @param y The y-coordinate of the point
    """
    self.x = x
    self.y = y
    self.color = color

class Circle:
  def __init__(self, x=0, y=0, radius=0, centroid=(0,0), color=color.Green):
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
    self.radius = radius
    self.centroid = centroid
    self.color = color


class Line:
  def __init__(self, x1=0, y1=0, x2=0, y2=0, length=0, color=color.Red,
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
    self.dx = (x1 - x2) * 1.0
    self.dy = (y1 - y2) * 1.0
    self.color = color
    self.thickness = thickness
    
    # Only calculate length if not already provided
    if length is 0:
      self.length = math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2, 2))
