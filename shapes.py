"""
@file Shapes.py

@brief The circle class, used for display and location
"""
import colors as color

class Circle:

  def __init__(self, x=0, y=0, radius=0, center=(0,0), color=color.Green):
    """
    @brief Sets up initial parameters

    @param x The x coordinate of the circle center. From finding minimum 
      enclosing circle.
    @param y the y coordinate of the circle center. From finding minimum
      enclosing circle.
    @param radius The radius of the circle
    @param center A tuple of (x,y) coordinates of the circle. Comes from 
      calcuation of center using moments.
    @param color The color to display the circle in
    """
    self.x = x
    self.y = y
    self.radius = radius
    self.center = center
    self.color = color