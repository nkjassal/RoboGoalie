import time # for fps counter
import colorsys

import numpy as np
import cv2 as cv2
from IPython import embed

class BallTracker:

  # for trackbar
  def nothing(self, x):
    pass

  def __init__(self, window_name='Object Tracking', scale=0.5, debug=0):
    # The name of the window to be displayed
    self.window_name = window_name
    cv2.namedWindow(self.window_name)
    self.scale = scale
    # The number of frames to average fps over
    self.FPS_FRAMES = 50


    self.hsv_blue_low = (75, 90, 90)
    self.hsv_blue_high = (135, 255, 255)
    # HSV FOR DECENT BLUE RANGE
   # self.hsv_blue_low = (80,220,100)
    #self.hsv_blue_high = (128,255,255)  

    self.debug = debug

  def track_ball(self, img):
    
    blur = cv2.GaussianBlur(img, (11,11), 0) # -0 frames
    img_hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Mask with range of HSV values - for blue, will return white where blue
    # is and black otherwise
    mask = cv2.inRange(img_hsv, self.hsv_blue_low, self.hsv_blue_high)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    # destructive, so copy mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    # only proceed if at least one contour found
    if len(cnts) > 0:
      # find largest contour in mask, then use it to compute min enclosing
      # circle and centroid
      c = max(cnts, key=cv2.contourArea)
      ((x,y), radius) = cv2.minEnclosingCircle(c)
      M = cv2.moments(c)

      # if divide by 0 will occur skip circle this frame
      if int(M["m00"]) is 0:
        return img
      center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

      # only proceed if radius meets certain size
      if radius > 10:
        # draw circle and centroid on frame
        cv2.circle(img, (int(x),int(y)), int(radius),
          (0,255,255), 2)
        cv2.circle(img, center, 5, (0,0,255), -1)


    return img

  """
  @brief Rescales and blurs frame for clarity and faster operations

  @param frame The frame to be operated on and returned
  @param scale The frame will be scaled multiplicatively by this much (0-1)
  @param blur_window The window size used for the median blur

  @return The updated frame
  """  
  def setup_frame(self, frame, scale=0.5, blur_window=11):

    h_scaled,w_scaled = tuple(scale * np.asarray(frame.shape[:2]))
   
    # scale is a tuple, not two separate arguments (w, h)
    frame = cv2.resize(frame, (int(w_scaled), int(h_scaled)), 
      cv2.INTER_LINEAR)

    cv2.flip(src=frame,dst=frame, flipCode=1) # flip across y for correctness

    # Median blur seems to be better for detecting edges, but is significantly 
    # slower than the gaussian blur (lose ~10fps at 0.5 scaling)
    #frame = cv2.GaussianBlur(frame, (blur_window,blur_window), 0) # -0 frames
    #frame = cv2.medianBlur(frame, blur_window) # -10 frames

    return frame

  def stream(self):
    # create video capture object for first video cam (mac webcam)
    cap = cv2.VideoCapture(0)

    # FPS Counters
    count = 0
    old_time = 0
    fps = '' # for display

    while(True):
      # start fps timer
      if count is 0:
        old_time = time.time()

      # Capture frame-by-frame, reduce image size to process faster
      ret, frame = cap.read()

      scaled = self.setup_frame(frame=frame, scale=self.scale, blur_window=11)
    
      frame = self.track_ball(scaled)

      #### FPS COUNTER ####
      # if correct number of frames have elapsed
      if count is self.FPS_FRAMES:
        elapsed_time = time.time() - old_time # get time elapsed
        fps_val = 1.0 * self.FPS_FRAMES / elapsed_time
        count = 0 # reset count
        fps = str(round(fps_val, 1))
      else:
       count += 1

      # Display FPS on screen
      font = cv2.FONT_HERSHEY_SIMPLEX # no idea what font this is
      cv2.putText(frame, fps, (10, 30), font, 0.8, (0,255,0),2,cv2.LINE_AA)


      # display resulting frame
      cv2.imshow(self.window_name,frame)

      if self.debug:
        cv2.moveWindow('Scaled Frame', 0,500)
        cv2.imshow('Scaled Frame', scaled)

      # quit option with q
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # release capture
    cap.release()
    cv2.destroyAllWindows()

def main():

  tracker = BallTracker(window_name='test', debug=0) 

  tracker.stream() # begin tracking and object detection

  


if __name__ == "__main__":
  main()

