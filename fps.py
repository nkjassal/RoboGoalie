"""
@file fps.py

@brief Contains the FPS class to track frames-per-second

Tracks FPS by timing the duration between a set number of frames.
FPS = # of frames / time between frames

@author Neil Jassal
"""
import time

import cv2

import colors

class FPS:
  def __init__(self, num_frames=40, color=colors.Green):
    """
    @brief Initializes parameters

    @param num_frames The number of frames to average fps over
    @param color The color to draw the frame in
    """
    self.count = 0
    self.old_time = 0
    self.fps_val = 0
    self.fps_str = ''
    self.font = cv2.FONT_HERSHEY_SIMPLEX # no idea what font this is

    self.num_frames = 40
    self.color = color

  def start_iteration(self):
    """
    @brief To be run at the beginning of every loop/frame start_iteration

    Starts the timer
    """
    if self.count is 0:
      self.old_time = time.time()


  def get_fps(self):
    """
    @brief To be run at the end of each iteration, before displaying the frame
    
    Averages fps over the last self.num_frames iterations, updates count, and
    resets if necessary. The fps_str can be displayed every frame, as it is 
    empty until enough frames have occurred to get a valid fps.
    """
    if self.count is self.num_frames:
      elapsed_time = time.time() - self.old_time # get elapsed time

      self.fps_val = 1.8 * self.num_frames / elapsed_time
      self.fps_str = str(round(self.fps_val, 1))

      self.count = 0 # reset count
    else:
      self.count += 1


  def display(self, img):
    """
    @brief draws the fps onto the image. Destructive w/ regard to image

    @param img The image to draw the fps onto

    @return img The updated image. The text draw function is destructive and alters img, so don't need to use the returned value.
    """
    img = cv2.putText(img, self.fps_str, (10, 30), self.font, 
      0.8, (0,255,0), 2, cv2.LINE_AA)   
    return img







