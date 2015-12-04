"""
@file trajectory.py

@brief Contains trajectory class used to predict object trajectories

Uses Points locations from n-previous frames to approximate a line of the 
current object trajectory. Trajectory estimation is using numpy.polyfit with 
a dimension of 1.

Note that a larger number of frames means a slower reaction - prediction will
not occur until n frames have been added to the list.

If an object is stationary, noise in the video or location feed may cause
noisy points to be added, resulting in incorrect and/or highly skewed best fit
lines.

The trajectory planner will also not directly handle switching to a new object
to track for the goalie. A few frames of noise (n frames) will occur while the
old location points are in the list with the newer ones.

@author Neil Jassal
"""

import cv2
import numpy as np

import shapes
import colors

class TrajectoryPlanner:
    def __init__(self, frames=2):
      """
      @brief Initializes parameters

      @param frames The number of previous points to fit the trajectory to
      """
      self.num_frames = frames

      # Index of most recent frame in pt_list. Iterated with modulo operator
      # to wrap properly and always use
      self.index = None
      self.pt_list = [None] * self.num_frames # list of Points
      # Separate x and y list are kept for convenience when fitting line
      self.x_list = [None] * self.num_frames  # list of x-values for best fit
      self.y_list = [None] * self.num_frames # list of y-values for best fit
      

      ######## FOR 2-FRAME TRAJECTORY ESTIMATION #########
      # The previous frame's point/circle. TODO: upgrade to an n-frame list
      self.prev_pt = None
      # The current frame's object point/circle TODO: upgrade to n-frame list
      self.curr_pt = None
      # The line representing the current trajectory
      self.traj = shapes.Line()


    def add_point(self, point):
      """
      @brief Adds current point to list of points, overwriting the oldest value

      For optimal usage, it is generally recommended to add a point denoting 
      the updated location at every frame

      @param The Point or Circle object to add as the current frame
      """
      if point is None:
        return

      if self.index is None: # first time
        self.index = 0
      else:
        # increment index so it wraps
        self.index = (self.index + 1) % self.num_frames

      self.pt_list[self.index] = point
      self.x_list[self.index] = point.x
      self.y_list[self.index] = point.y

    def get_trajectory(self, color=colors.Cyan):
      """
      @brief Gets best fit line from n-previous points

      Uses np.polyfit with dimension 1. Creates line from two points. Points
      are generated using closest point to most recent frame (x1,y1) and 
      a point (x1 + 1.0, y2)

      @param color The color to be used in the trajectory line

      @return ln Line object representing the trajectory
      """
      # Not enough frames collected
      if None in self.pt_list:
        return None

      # get best fit line
      fit = np.polyfit(self.x_list, self.y_list, 1, full=True)
      m = fit[0][0] # slope of best fit line
      b = fit[0][1] # intercept of best fit line

      x1 = self.x_list[self.index]
      x2 = x1 + 1.0
      y1 = m * x1 + b
      y2 = m * x2 + b


      ln = shapes.Line(x1=x1, y1=y1, x2=x2, y2=y2, color=color)
      return ln


    ######## FOR 2-FRAME TRAJECTORY ESTIMATION #########
    def update_frames(self, point):
      """
      @brief Adds the current point to the list of points to get traj from

      Should be run every time a new point is found

      @param point The current Point or Circle object found
      """
      # Move now-old point to previous and update current point
      self.prev_pt = self.curr_pt
      self.curr_pt = point

    def get_traj(self, color=colors.Cyan):
      """
      @brief Uses the n-frame list to determine the current trajectory

      @param color The trajectory Line color to use

      @return traj The Line object, direction is pt1 to pt2
      """
      if self.prev_pt is None or self.curr_pt is None:
        return None
      ln = shapes.Line(x1=self.prev_pt.x, y1=self.prev_pt.y,
        x2=self.curr_pt.x, y2=self.curr_pt.y, color=color)

      return ln



