import time # for fps counter

import numpy as np
import cv2 as cv2
from IPython import embed


class BallTracker:

  def __init__(self, window_name, scale=0.5):
    # The name of the window to be displayed
    self.window_name = window_name
    self.scale = scale
    # The number of frames to average fps over
    self.FPS_FRAMES = 50


  # for trackbar
  def nothing(self, x):
    pass

  def track_ball(self, img):

    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    # lower_blue = np.array([110, 50, 50])
    # upper_blue = np.array([130, 255, 255])

    # # threshold hsv image to only get blue
    # mask = cv2.inRange(hsv, lower_blue, upper_blue)

    #### USING TRACKBARS $$$$
     


    return img_hsv

  """
  @brief Rescales and blurs frame for clarity and faster operations

  @param frame The frame to be operated on and returned
  @param scale The frame will be scaled multiplicatively by this much (0-1)
  @param blur_window The window size used for the median blur

  @return The updated frame
  """  
  def setup_frame(self, frame, scale, blur_window):

    h_scaled,w_scaled = tuple(scale * np.asarray(frame.shape[:2]))
   
    # scale is a tuple, not two separate arguments (w, h)
    frame = cv2.resize(frame, (int(w_scaled), int(h_scaled)), 
      cv2.INTER_LINEAR)

    cv2.flip(src=frame,dst=frame, flipCode=1) # flip across y for correctness

    # Median blur seems to be better for detecting edges, but is significantly 
    # slower than the gaussian blur (lose ~10fps at 0.5 scaling)
    frame = cv2.GaussianBlur(frame, (blur_window,blur_window), 0) # -0 frames
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

      frame = self.setup_frame(frame=frame, scale=self.scale, blur_window=15)
    


      #img = track_ball(img)




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
      cv2.putText(frame, fps, (10, 30), font, 0.8, (0,0,255),2,cv2.LINE_AA)


      # display resulting frame
      cv2.imshow(self.window_name,frame)

      # quit option with q
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # release capture
    cap.release()
    cv2.destroyAllWindows()

def main():

  tracker = BallTracker(window_name='test') 

  tracker.stream() # begin tracking and object detection

  


if __name__ == "__main__":
  main()

