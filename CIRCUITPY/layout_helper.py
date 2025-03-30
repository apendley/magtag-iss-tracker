from adafruit_display_text import wrap_text_to_pixels
import fonts
from collections import namedtuple

FormatLocationResult = namedtuple("FormatLocationResult", ["lines", "font", "line_height"])

class LayoutHelper:
    def __init__(self, display_width, display_height):
        self._display_width = display_width
        self._display_height = display_height

    @property
    def display_width(self):
        return self._display_width

    @property
    def display_height(self):
        return self._display_height
    
    @property
    def map_width(self):
        return 192

    @property
    def map_height(self):
        return 128

    @property
    def map_x_offset(self):
        return self._display_width - self.map_width

    @property
    def equator_y(self):
        return self.map_height // 2

    @property
    def meridian_x(self):
        return self.map_width // 2

    @property
    def text_left_margin(self):
        return 2

    @property
    def home_icon_radius(self):
        return 4

    @property
    def iss_icon_radius(self):
        return 4

    @property
    def history_marker_radius(self):
        return 3

    @property
    def distance_bg_height(self):
        return 43

    @property
    def distance_label_x_center(self):
        return self.map_x_offset // 2 - 2

    @property
    def distance_units_y_offset(self):
        return self.distance_bg_height - 15

    @property
    def location_name_y_offset(self):
        return 54

    @property
    def timestamp_y_offset(self):
        return 120

    @property
    def timestamp_bg_height(self):
        return 15

    def lat_lon_to_screen(self, lat, lon):
        meridian_offset_px = abs(lon) * (self.map_width / 360)
        screen_x = (round(self.meridian_x - meridian_offset_px if lon < 0 else self.meridian_x + meridian_offset_px)) + self.map_x_offset

        equator_offset_px = abs(lat) * (self.map_height / 180)
        screen_y = round(self.equator_y - equator_offset_px if lat >= 0 else self.equator_y + equator_offset_px)

        return screen_x, screen_y

    def format_location(self, text):
        # If any words exceed the max width, shrink the font to fit it in one line, if possible.
        if self._has_word_exceeding_max_width(text, fonts.REGULAR_14):
            print("Format location: shrink-to-longest-word level 2")

            if self._has_word_exceeding_max_width(text, fonts.BOLD_10):
                print("Format location: shrink-to-longest-word level 3")

                if self._has_word_exceeding_max_width(text, fonts.BOLD_10):
                    # At this point, we're already at the smallest font,
                    # and we still can't fit one of the words on a single line,
                    # so let's just go ahead and let phase 2 give it a shot,
                    # since the worst case scenario is the same either way.
                    print("Format location: shrink-to-longest-word failed, falling back to shrink-to-fit")
                else:
                    return self._format_shrink_to_fit(text, fonts.BOLD_8)
            else:
                # The word fits with the smaller font, let's use it
                return self._format_shrink_to_fit(text, fonts.BOLD_10)

        # Now try to perform word wrapping on the text, shrinking to fit if we exceed our width,
        # and truncating the final string with an ellipsis if we cannot fit the text within the space.
        result = self._format_shrink_to_fit(text, fonts.REGULAR_14)

        if result is None:
            print("Format location: shrink-to-fit level 2")
            result = self._format_shrink_to_fit(text, fonts.BOLD_10)

        if result is None:
            print("Format location: shrink-to-fit level 3")
            result = self._format_shrink_to_fit(text, fonts.BOLD_8, truncate=True)

        return result


    # Check to see if any of the individual words exceed the width,
    # and if so, move down a font size
    def _has_word_exceeding_max_width(self, text, font):
        max_width = self._display_width - self.map_width - self.text_left_margin
        words = text.split(" ")

        for word in words:
            lines = wrap_text_to_pixels(
                word,
                max_width=max_width,
                font=font
            )

            if len(lines) > 1:
                return True

        return False

    def _format_shrink_to_fit(self, text, font, truncate=False):
        if font == fonts.REGULAR_14:
            max_lines = 4
            line_height = 20
        elif font == fonts.BOLD_10:
            max_lines = 5
            line_height = 16
        else:
            max_lines = 6
            line_height = 13

        max_width = self._display_width - self.map_width - self.text_left_margin

        try:
            lines = wrap_text_to_pixels(
                text,
                max_width=max_width,
                font=font
            )

            if len(lines) <= max_lines:
                return FormatLocationResult(lines, font, line_height)
            elif truncate:
                lines = lines[:max_lines]
                last_line = lines[-1]

                if len(last_line) >= 3:
                    last_line = last_line[:-3]
                    last_line += "..."
                    lines[-1] = last_line

                return FormatLocationResult(lines, font, line_height)
            else:
                return None

        except Exception as err:
            print(f"Error formatting location name: {err}")
            return None
