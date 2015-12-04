"""
@file trajectory.py

@brief Contains trajectory class used to predict object trajectories

Uses Points locations from n-previous frames to approximate a line of the 
current object trajectory.

@author Neil Jassal
"""

import cv2

import shapes
import colors

class TrajectoryPlanner:
    def __init__(self, frames=2):
      """
      @brief Initializes parameters

      @param frames The number of previous points to fit the trajectory to
      """
      self.num_frames is 0

      # Index of most recent frame in pt_list. Iterated with modulo operator
      # to wrap properly and always use
      self.start_index = None
      self.pt_list = [None] * num_frames # list of Points
      # Separate x and y list are kept for convenience when fitting line
      self.x_list = [None] * num_frames  # list of x-values for best fit
      self.y_list = [None] * num_frames # list of y-values for best fit
      

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

      @param The Point or Circle object to add as the current frame
      """
      if point is None:
        return

      if self.start_index is None: # first time
        self.start_index = 0
      else:
        # increment index so it wraps
        self.start_index = (self.start_index + 1) % self.num_frames

      self.pt_list[self.start_index] = point
      self.x_list[self.start_index] = point.x
      self.y_list[self.start_index] = point.y







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



