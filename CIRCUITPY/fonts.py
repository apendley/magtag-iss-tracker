from adafruit_bitmap_font import bitmap_font
from displayio import Bitmap

from terminalio import FONT as REGULAR_8

NUMERIC_24 = bitmap_font.load_font("assets/fonts/helvR24-num.pcf", Bitmap)
REGULAR_14 = bitmap_font.load_font("assets/fonts/helvR14.pcf", Bitmap)
BOLD_8 = bitmap_font.load_font("assets/fonts/helvB08.pcf", Bitmap)
BOLD_10 = bitmap_font.load_font("assets/fonts/helvB10.pcf", Bitmap)
