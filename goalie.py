"""
@file goalie.py

@brief Main script for tracking, displaying and moving robot

@author Neil Jassal
"""
import time # for fps counter

import cv2
import numpy as np

import BallTracker as bt
import colors as color
import shapes

def stream(tracker, camera=0):
  """ 
  @brief Captures video and runs tracking and moves robot accordingly

  @param tracker The BallTracker object to be used
  @param camera The camera number (0 is default) for getting frame data
  """
  # create video capture object for
  cap = cv2.VideoCapture(0)
  cv2.namedWindow(tracker.window_name)

  # FPS Counters
  count = 0
  old_time = 0
  fps = '' # for display

  while(True):
    # start fps timer
    if count is 0:
      old_time = time.time()

    #### CAPTURE AND PROCESS FRAME ####
    ret, frame = cap.read()
    frame,img_hsv = tracker.setup_frame(frame=frame, blur_window=11)



    #### TRACK OBJECTS ####
    # use the HSV image to get Circle objects for robot and objects
    object_list = tracker.find_circles(img_hsv.copy(), tracker.track_colors,
      tracker.num_per_color)
    robot_pos = tracker.find_robot(img_hsv.copy(), tracker.robot_color)

    # Only run tracking calculations if both markers found
    if (len(robot_pos) < 2) or robot_pos is None:
      pass
    else:
      robot_axis = shapes.Line(robot_pos[0].x, robot_pos[0].y,
        robot_pos[1].x, robot_pos[1].y)



    #### DRAW CIRCLES AROUND OBJECTS ####
    frame = tracker.draw_circles(frame, object_list)
    if robot_pos is not None:
      frame = tracker.draw_robot_markers(frame, robot_pos)


    #### FPS COUNTER ####
    # if correct number of frames have elapsed
    if count is tracker.FPS_FRAMES:
      elapsed_time = time.time() - old_time # get time elapsed
      fps_val = 1.0 * tracker.FPS_FRAMES / elapsed_time
      count = 0 # reset count
      fps = str(round(fps_val, 1))
    else:
     count += 1

    #### DISPLAY FRAME ON SCREEN ####
    # Display FPS on screen every frame
    font = cv2.FONT_HERSHEY_SIMPLEX # no idea what font this is
    cv2.putText(frame, fps, (10, 30), font, 0.8, (0,255,0),2,cv2.LINE_AA)

    # display resulting frame
    cv2.imshow(tracker.window_name,frame)

    # quit by pressing q
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # release capture
  cap.release()
  cv2.destroyAllWindows()



def main():
  """ 
  @brief Initializes the tracker object and runs goalie script
  """    
  robot_color = color.Blue
  track_colors = []#[color.Blue]
  tracker = bt.BallTracker(
    window_name="Robot Goalie Display",
    robot_color=robot_color, 
    track_colors=track_colors, 
    radius=15,
    num_per_color = 2) 

  stream(tracker) # begin tracking and object detection



if __name__ == "__main__":
  main()