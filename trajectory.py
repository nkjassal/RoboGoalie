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
    def __init__(self):
      """
      @brief Initializes parameters
      """
      # The previous frame's point/circle. TODO: upgrade to an n-frame list
      self.prev_pt = None
      # The current frame's object point/circle TODO: upgrade to n-frame list
      self.curr_pt = None
      # The line representing the current trajectory
      self.traj = shapes.Line()


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



