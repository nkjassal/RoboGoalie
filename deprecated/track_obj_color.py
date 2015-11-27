# TEST FILE - DOES NOT PROVIDE ANY FUNCTIONALITY

import numpy as np
import cv2 as cv2
from IPython import embed

def nothing(*arg):
  pass

def track_stream():
  # create video capture object for first video cam (mac webcam)
  cap = cv2.VideoCapture(0)

  img_low = np.zeros((15,512,3), np.uint8)
  img_high = np.zeros((15,512,3), np.uint8)

  cv2.namedWindow('BGR_low')
  cv2.imshow('BGR_low',img_low)
  cv2.namedWindow('BGR_high')
  cv2.imshow('BGR_high',img_high)

  cv2.createTrackbar('R','BGR_low',50,255,nothing)
  cv2.createTrackbar('G','BGR_low',50,255,nothing)
  cv2.createTrackbar('B','BGR_low',110,255,nothing)
  cv2.createTrackbar('R','BGR_high',255,255,nothing)
  cv2.createTrackbar('G','BGR_high',255,255,nothing)
  cv2.createTrackbar('B','BGR_high',130,255,nothing)

  while(True):
    # Capture frame-by-frame, cut image size in half to process faster
    ret, frame = cap.read()
    
    r_low = cv2.getTrackbarPos('R','BGR_low')
    g_low = cv2.getTrackbarPos('G','BGR_low')
    b_low = cv2.getTrackbarPos('B','BGR_low')
    r_high = cv2.getTrackbarPos('R','BGR_high')
    g_high = cv2.getTrackbarPos('G','BGR_high')
    b_high = cv2.getTrackbarPos('B','BGR_high')
    img_low[:] = [b_low,g_low,r_low]
    img_high[:] = [b_high,g_high,r_high]

    cv2.imshow('BGR_low',img_low)
    cv2.imshow('BGR_high',img_high)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([b_low,g_low,r_low])
    upper_blue = np.array([b_high,g_high,r_high])


    mask_image = cv2.inRange(hsv, lower_blue, upper_blue)
    cv2.imshow('BGR High', mask_image)
    
    result_image = cv2.bitwise_and(frame,frame, mask= mask_image)
    cv2.imshow('BGR Low', result_image)

    # display resulting frame
    #cv2.imshow('frame',img)

    # quit option with q
    if cv2.waitKey(1) & 0xFF == ord('q'):
      return

def main():

  track_stream() # begin tracking and object detection

  # release capture
  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()

