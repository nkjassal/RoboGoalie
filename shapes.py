"""
@file Shapes.py

@brief The circle class, used for display and location
"""
import colors as color

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
      calcuation of centroid   using moments.
    @param color The color to display the circle in
    """
    self.x = x
    self.y = y
    self.radius = radius
    self.centroid = centroid
    self.color = color