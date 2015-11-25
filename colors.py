"""
@name colors.py

@brief A list of colors and associated hsv bounds

Contains HSV ranges for the following colors:
  Blue,

For HSV color detection, the lower and upper bounds must be called 'lower' and
'upper', respectively.

When determining HSV colors, it is important to note that OpenCV uses:
  H from 0 to 180
  S from 0 to 255
  V from 0 to 255

TODO: red, orange, black, white, green, yellow
"""

class Blue:
  lower = (75, 90, 90)
  upper = (135, 255, 255)

class Orange:
  lower = (5, 90, 90)
  upper = (25, 255, 255)