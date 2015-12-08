"""
@file trajectory.py

@brief Contains trajectory class used to predict object trajectories

Uses Points locations from n-previous frames to approximate a line of the 
current object trajectory. Trajectory estimation is using numpy.polyfit with 
a dimension of 1. Trajectories are created in the direction of the robot_axis

For multiple bounces, trajectory estimation will produce a list of Line objects
representing each 'bounce.' The last element of this list is the line of the
final predicted trajectory (after n bounces)

Note that a larger number of frames means a slower reaction - prediction will
not occur until n frames have been added to the list.

If an object is stationary, noise in the video or location feed may cause
noisy points to be added, resulting in incorrect and/or highly skewed best fit
lines.

The trajectory planner will also not directly handle switching to a new object
to track for the goalie. A few frames of noise (n frames) will occur while the
old location points are in the list with the newer ones.

Standard usage for a 3-frame best fit model (pseudocode example)::

planner = TrajectoryPlanner(3)
while True:
  frame = get_video_frame()
  point = frame.get_object_location() # point is a shapes.Point object
  # Every frame, add the newest point
  planner.add_point(point)
  # Returns None until 3 frames have been added, then returns shapes.Line
  traj = planner.get_trajectory()

@author Neil Jassal
"""
import math

import cv2 # 3rd party imports
import numpy as np

import shapes
import colors
import utils

class TrajectoryPlanner:
    def __init__(self, frames=5, bounces=0, walls=[], robot_axis=None):
      """
      @brief Initializes parameters

      @param frames The number of previous points to fit the trajectory to
      @param bounces How many bounces off of walls to predict
      @param walls A list of Line objects representing walls to bounce off of
      @param robot_axis The robot axis to be used
      """
      self.num_frames = frames
      self.num_bounces = bounces

      ######## SCENE DEFINITION PARAMETERS #########
      # Line objects representing walls for bounce prediction
      self.walls = walls
      # Line representing robot axis
      self.robot_axis = robot_axis

      ######### BEST FIT PARAMETERS ########
      # Index of most recent frame in pt_list. Iterated with modulo operator
      # to wrap properly and always use
      self.index = None
      self.pt_list = [None] * self.num_frames # list of Points
      # Separate x and y list are kept for convenience when fitting line
      self.x_list = [None] * self.num_frames  # list of x-values for best fit
      self.y_list = [None] * self.num_frames # list of y-values for best fit

      self.curr_index = None # Index of most recent point
      self.last_index = None # Index of oldest point
      
      ######## OUTPUT PARAMETERS ########
      # The final line of the trajectory, extending to the robot axis
      self.traj = None
      # List of lines representing all bounces of the trajectory prediction
      self.traj_list = []


    def add_point(self, point):
      """
      @brief Adds current point to list of points, overwriting the oldest value

      For optimal usage, it is generally recommended to add a point denoting 
      the updated location at every frame. A Point contains an x and y value

      @param The Point or Circle object to add as the current frame
      """
      if point is None:
        return

      if self.index is None: # first time
        self.index = 0
        self.curr_index = 0
      else:
        # increment index so it wraps, as well as current and last index
        self.index = (self.index + 1) % self.num_frames
        self.curr_index = self.index
        self.last_index = (self.index + 1) % self.num_frames

      self.pt_list[self.index] = point
      self.x_list[self.index] = point.x
      self.y_list[self.index] = point.y


    def add_wall(self, wall):
      """
      @brief Adds a wall to the trajectory's list
      @param wall A Line object representing the wall
      """
      if wall is None:
        return
      self.walls.append(wall)
      return


    def add_walls(self, wall_list):
      """
      @brief Adds a set of walls to the trajectory's list
      @param wall_list A list of Line objects representing walls
      """
      if wall_list is None:
        return
      for wall in wall_list:
        if wall is None:
          continue
        self.walls.append(wall)
      return


    def get_best_fit_line(self, color=colors.Cyan):
      """
      @brief Gets and returns a Line object representing the best fit line
      @param The color for the best fit line
      @return A Line object
      """
      # get best fit line
      fit = np.polyfit(self.x_list, self.y_list, 1, full=True)
      m = fit[0][0] # slope of best fit line
      b = fit[0][1] # intercept of best fit line

      x1 = self.x_list[self.index] # most recent x
      x2 = x1 + 1.0
      y1 = m * x1 + b
      y2 = m * x2 + b

      ln = shapes.Line(x1=x1, y1=y1, x2=x2, y2=y2, color=color)
      return ln


    def get_trajectory_list(self, color=colors.Cyan):
      """
      @brief Gets best fit traj from n-previous points and predicts bounces

      Uses np.polyfit with dimension 1. Creates line from two points. Points
      are generated using closest point to most recent frame (x1,y1) and 
      a point (x1 + 1.0, y2). This works as a line can be represented by any
      arbitrary two points along it. The actual points do not matter here or
      for the goalie, unless specified/calculated otherwise.

      self.traj is always the farthest-predicted line between the last impact
      point or object location and the robot axis

      self.traj_list contains, from oldest to farthest predicted, a list of 
      Lines representing each bounce. The lines go obj->wall, wall->wall, ...,
      wall->robot_axis.

      @param color The color to be used in the trajectory lines

      @return list of Line objects representing trajectory path
      """
      # Not enough frames collected
      if None in self.pt_list:
        return []

      # reset and get best fit line
      self.traj_list = []
      ln = self.get_best_fit_line()

      # get trajectory towards robot axis, line from obj to axis
      # if trajectory not moving towards robot axis, no prediction
      if not self.traj_dir_toward_line(self.robot_axis):
        ln = None
      start_pt = self.pt_list[self.curr_index]
      traj_int_pt = utils.line_intersect(ln, self.robot_axis) # Point object
      traj = utils.get_line(start_pt, traj_int_pt, color=colors.Cyan)
      self.traj = traj


      # return straight-line trajectory (as a 1-elem list for consistency) if
      # no bounces to be predicted
      if self.num_bounces is 0: # no bounces
        self.traj_list.append(ln)
        return self.traj_list

      for wall in self.walls:
        # Determine where bounce occurs and add line up to bounce
        bounce_pt = utils.line_segment_intersect(self.traj, wall)
        if bounce_pt is None:
          continue

        bounce_ln = utils.get_line(self.pt_list[self.curr_index],
          bounce_pt, color=colors.Cyan)
        self.traj_list.append(bounce_ln)


        ### THIS IS BROKEN LOL
        # Reflect line across wall and project to next wall or axis
        # Slope = dy/dx --> reflected slope -dx/dy, slope -> -1/slope
        reflect_dx = -1.0
        reflect_dy = 0
        if math.fabs(bounce_ln.slope) < 0.0001: # avoid divide by 0
          reflect_dy = 0.0001
        else:
          reflect_dy = bounce_ln.slope

        #### ONCE NEW DX AND DY ARE FOND, IT WORKS. GETTING DX/DY FAILS ####
        new_x = bounce_pt.x + reflect_dx * 0.001
        new_y = bounce_pt.y + reflect_dy * 0.001
        new_pt = shapes.Point(new_x, new_y)
        new_ln = utils.get_line(bounce_pt, new_pt) # small line
        final_int = utils.line_intersect(new_ln, self.robot_axis)
        final_ln = shapes.Line(x1=bounce_pt.x, y1=bounce_pt.y,
          x2=final_int.x, y2=final_int.y, color=colors.Cyan)
        self.traj_list.append(final_ln)

        break

      return self.traj_list


    def get_trajectory(self, calculate=1, color=colors.Cyan):
      """
      @brief Gets the full list of trajectory prediction lines, and returns
      a line for the final trajectory

      @param calculate Whether to compute the trajectory or take from list
      @param color The color of trajectory lines

      @return The last predicted trajectory line
      """
      if calculate is 1:
        self.traj_list = self.get_trajectory_list(color)

      # if failed to get trajectory list
      if self.traj_list is None:
        return None
      if len(self.traj_list) < 1:
        return None

      # return last predicted line - best prediction
      return self.traj_list[len(self.traj_list) - 1]


    def traj_dir_toward_line(self, line):
      """
      @brief Determines if the current trajectory is moving toward the line

      Takes the most and least recent points, and determines if the overall
      direction of the trajectory is generally toward the given Line or away.
      This is done by comparing the distance between the current point and 
      oldest point. 

      In context of the robot goalie, will determine if the robot is currently
      moving towards the robot axis, irrespective of bounces. Used to tell
      if the ball is generally moving towards or away from the axis
        
        if dist(curr_pt to line) < dist(old_pt to line):
          return 1
        else return 0

      @param line The Line object used

      @return 1 if moving towards line, 0 if not
      """
      if None in self.pt_list or line is None:
        return 0

      curr_pt = self.pt_list[self.curr_index]
      last_pt = self.pt_list[self.last_index]

      unused, distances = utils.distance_from_line(
        [curr_pt, last_pt], line, squared=1)

      # current point is closer to line than last point
      if distances[0] < distances[1]:
        return 1

      return 0





