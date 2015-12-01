"""
@file colors.py

@brief A list of colors and associated hsv bounds and bgr value

Contains HSV ranges for the following colors:
  Blue, Green, Red, White

Contains BGR values for the following colors:
  Blue, Green, Red, White, Yellow, Magenta, Cyan

HSV color detection by using two sets of range. Due to how HSV values work,
colors on the red spectrum have Hue values that wrap (H=179 and H=0 are both 
red). As such, two sets of bounds can be specified on the ranges:
[lower0, upper0]
[lower1, upper1]

If only one color range is needed, use lower0 and upper0, then lower1 and
upper1 will be the tuple (0,0,0)

When determining HSV colors, it is important to note that OpenCV uses the
following color ranges when HSV is calculated with the cv2.COLOR_BGR2HSV macro:
  H from 0 to 180
  S from 0 to 255
  V from 0 to 255

NOTE: For standard colors with an Hue of H, a decent color range seems
(on the 0 to 180 scale) to be approximately:
 (H - 44) to (H + 44)

TODO: TRY (H +/- 30) - MEANS NO COLOR BLUE,GREEN,RED OVERLAPS

The +/- scale of 22 works alright as well.

NOTE: The Saturation value S should be specifically determined on a 
color-by-color basis. S=90 or S=150 seem to work decently, as starting points.

@author Neil Jassal

"""

class Blue:
  """
  @brief HSV range for blue. H = 119
  Works well
  """
  bgr = (255,0,0)

  lower0 = (75, 90, 90)
  upper0 = (163, 255, 255)
  lower1 = (0,0,0) # no second range needed
  upper1 = (0,0,0)


class Green:
  """
  @brief BGR and HSV range for green. H = 60
  """
  bgr = (0,255,0)

  lower0 = (16, 90, 90)
  upper0 = (104, 255, 255)
  lower1 = (0,0,0)  # no second range needed
  upper1 = (0,0,0)


class Red:
  """
  @brief BGR and HSV range for red. H = 0
  """
  bgr = (0,0,255)

  lower0 = (0, 150, 150)
  upper0 = (20, 255, 255)
  lower1 = (160, 150, 150)
  upper1 = (179,255, 255)


class White:
  """
  @brief BGR and HSV range for white. 
  Works alright, but other objects in high light environments can also be
  detected as white, causing potential problems.
  """
  bgr = (255, 255, 255)

  lower0 = (0, 0, 220)
  upper0 = (180, 50, 255)
  lower1 = (0,0,0) # no second range needed
  upper1 = (0,0,0)


class Yellow:
  """
  @brief BGR and HSV range for yellow. 
  TODO: Add upper/lower bounds
  """
  bgr = (0, 255, 255)


class Magenta:
  """
  @brief BGR and HSV range for magenta.
  TODO: Add upper/lower bounds
  """
  bgr = (255, 0, 255)


class Cyan:
  """
  @brief GBR and HSV range for cyan.
  TODO: Add upper/lower bounds
  """
  bgr = (255, 255, 0)




