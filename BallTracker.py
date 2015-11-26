import time # for fps counter

import numpy as np
import cv2 as cv2
from IPython import embed # for debugging

import colors as color # application-specific constants

class BallTracker:

  def __init__(self, window_name='Object Tracking', scale=0.5, 
    robot_marker=color.Red, track_colors=[color.Blue], radius=10, debug=0):
    """
    @brief inits default tracking parameters

    @param window_name The name of the window to be displayed on screen
    @param scale Webcam frame gets scaled by this much (0 to 1).
    @param robot_marker The color (from colors.py) of the robot marker
    @param track_colors List of colors (from colors.py) to be tracked. 
      TODO: SUPPORT MULTIPLE COLORS IN A LIST
    @param radius The min radius circle to be detected
    """

    # if robot marker and track color are the same, won't be able to tell apart
    if robot_marker in track_colors:
      print 'Unable to discern robot marker from some objects (same color). Ensure robot marker color is different from colors to be tracked'
      exit()

    # The name of the window to be displayed
    self.window_name = window_name
    cv2.namedWindow(self.window_name)
    self.scale = scale

    # The number of frames to average fps over
    self.FPS_FRAMES = 50

    self.robot_marker = robot_marker
    self.track_colors = track_colors

    self.debug = debug


  def draw_circles(self, img, circle_list):
    """
    @brief Draws circles/centroid from the given circle list onto the frame

    @param img The image to have circles drawn on
    @param circle_list List of tuples containing (x,y,radius)

    @return img The updated image with drawn circles
    """
    for circle in circle_list:
      x,y,radius,center = circle[0], circle[1], circle[2], circle[3]
      cv2.circle(img, (int(x),int(y)), int(radius),
        (0,255,255), 2)
      cv2.circle(img, center, 5, (0,0,255), -1) # centroid   

    return img

  def find_circles(self, img_hsv):
    """
    @brief Finds circle(s) in the frame based on input params, displays 
    on-screen

    Detects circles of the given minimum radius, displays a circle around them 
    and the centroid of each.

    @param img_hsv The frame in HSV to detect circles in

    @return circle_list List of detected circles (x,y,radius,center)
    #@return img The processed frame with circles drawn on it
    """
    circle_list = []

    for color in self.track_colors:
      # Mask with range of HSV values - for blue, will return white where blue
      # is and black otherwise. Uses both color bounds and combines.
      mask = cv2.bitwise_or(
        cv2.inRange(img_hsv, color.lower0, color.upper0),
        cv2.inRange(img_hsv, color.lower1, color.upper1))

      # reduce noise
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
          circle_list.append((int(x), int(y), int(radius), center))


    return circle_list


  def setup_frame(self, frame, scale=0.5, blur_window=11):
    """
    @brief Rescales and blurs frame for clarity and faster operations

    @param frame The frame to be operated on and returned
    @param scale The frame will be scaled multiplicatively by this much (0-1)
    @param blur_window The window size used for the median blur

    @return The updated frame
    @return The updated frame blurred and in hsv
    """  
    # scale is a tuple, not two separate arguments (w, h)
    h_scaled,w_scaled = tuple(self.scale * np.asarray(frame.shape[:2]))
    frame = cv2.resize(frame, (int(w_scaled), int(h_scaled)), 
      cv2.INTER_LINEAR)
    cv2.flip(src=frame,dst=frame, flipCode=1) # flip across y for correctness

    blur = cv2.GaussianBlur(frame, (blur_window,blur_window), 0) # -0 frames
    img_hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    return frame, img_hsv


  def stream(self):
    """ 
    @brief Runs video capture and tracking with FPS counter
    """
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

      # Capture frame-by-frame and process
      ret, frame = cap.read()
      frame,img_hsv = self.setup_frame(frame=frame, blur_window=11)

      # use the HSV image to detect circles, then draw on the original frame
      circle_list = self.find_circles(img_hsv)
      frame = self.draw_circles(frame, circle_list)

      #### FPS COUNTER ####
      # if correct number of frames have elapsed
      if count is self.FPS_FRAMES:
        elapsed_time = time.time() - old_time # get time elapsed
        fps_val = 1.0 * self.FPS_FRAMES / elapsed_time
        count = 0 # reset count
        fps = str(round(fps_val, 1))
      else:
       count += 1


      #### DISPLAY FRAME ON SCREEN ####
      # Display FPS on screen every frame
      font = cv2.FONT_HERSHEY_SIMPLEX # no idea what font this is
      cv2.putText(frame, fps, (10, 30), font, 0.8, (0,255,0),2,cv2.LINE_AA)

      # display resulting frame
      cv2.imshow(self.window_name,frame)

      # quit option with q
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # release capture
    cap.release()
    cv2.destroyAllWindows()



def main():
  """ Initializes the tracker object and Runs
  """    
  track_colors = [color.Blue, color.Red]
  tracker = BallTracker(robot_marker=color.White, track_colors=track_colors, 
    radius=10) 

  tracker.stream() # begin tracking and object detection

  


if __name__ == "__main__":
  main()

