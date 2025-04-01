from adafruit_bitmap_font import bitmap_font
from displayio import Bitmap

from terminalio import FONT as REGULAR_8
REGULAR_12 = bitmap_font.load_font("assets/fonts/new-science-medium-12.bdf", Bitmap)

NUMERIC_32 = bitmap_font.load_font("assets/fonts/new-science-medium-numeric-32.bdf", Bitmap)
NUMERIC_28 = bitmap_font.load_font("assets/fonts/new-science-medium-numeric-28.bdf", Bitmap)

LOCATION_LARGE = bitmap_font.load_font("assets/fonts/new-science-medium-21.bdf", Bitmap)
LOCATION_MEDIUM = bitmap_font.load_font("assets/fonts/new-science-medium-16.bdf", Bitmap)
LOCATION_SMALL = bitmap_font.load_font("assets/fonts/new-science-medium-13.bdf", Bitmap)
