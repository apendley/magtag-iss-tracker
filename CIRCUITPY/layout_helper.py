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
    def info_panel_width(self):
        return self._display_width - self.map_width - self.text_left_margin

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
        return 4

    @property
    def distance_bg_height(self):
        return 42

    @property
    def distance_label_x_center(self):
        return self.map_x_offset // 2

    @property
    def distance_label_y_center(self):
        return 15

    @property
    def distance_units_y_offset(self):
        return self.distance_bg_height - 13

    @property
    def location_name_y_offset(self):
        return 52

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

    # return the appropriate units label for the currently displayed units
    def units_text(self, use_miles):
        return "miles away" if use_miles else "km away"

    def format_location(self, text):
        result = None

        # First, see if any words in the string are too long to fit on one line.
        largest_word_font = self._font_for_largest_word(text)

        # If largest_word_font is None, there were no words too long. 
        # Otherwise, we'll use the returned font.
        if largest_word_font is not None:
            truncate = (largest_word_font == fonts.LOCATION_SMALL)
            result = self._format_shrink_to_fit(text, largest_word_font, truncate=truncate)

        # Now try to perform word wrapping on the text, shrinking to fit if we exceed our width,
        # and truncating the final string with an ellipsis if we cannot fit the text within the space.
        if result is None:
            result = self._format_shrink_to_fit(text, fonts.LOCATION_LARGE)

        if result is None:
            print("Format location: shrink-to-fit level 2")
            result = self._format_shrink_to_fit(text, fonts.LOCATION_MEDIUM)

        if result is None:
            print("Format location: shrink-to-fit level 3")
            result = self._format_shrink_to_fit(text, fonts.LOCATION_SMALL, truncate=True)

        return result

    def font_for_distance_text(self, distance_text):
        distance_font = fonts.NUMERIC_32

        lines = wrap_text_to_pixels(
            distance_text,
            max_width=self.info_panel_width,
            font=fonts.NUMERIC_32
        )

        return fonts.NUMERIC_28 if len(lines) > 1 else fonts.NUMERIC_32

    # Check to see if any of the individual words exceed the width,
    # and if so, move down a font size
    def _has_word_exceeding_max_width(self, text, font):
        max_width = self.info_panel_width
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

    def _font_for_largest_word(self, text):
        if not self._has_word_exceeding_max_width(text, fonts.LOCATION_LARGE):
            return fonts.LOCATION_LARGE

        print("Format location: shrink-to-longest-word level 2")
        if not self._has_word_exceeding_max_width(text, fonts.LOCATION_MEDIUM):
            return fonts.LOCATION_MEDIUM

        print("Format location: shrink-to-longest-word level 3")
        if not self._has_word_exceeding_max_width(text, fonts.LOCATION_SMALL):
            return fonts.LOCATION_SMALL            

        print("Format location: shrink-to-longest-word failed")
        return None

    def _format_shrink_to_fit(self, text, font, truncate=False):
        if font == fonts.LOCATION_LARGE:
            max_lines = 4
            line_height = 21
        elif font == fonts.LOCATION_MEDIUM:
            max_lines = 5
            line_height = 17
        else:
            max_lines = 6
            line_height = 14

        max_width = self.info_panel_width

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

                last_line_components = wrap_text_to_pixels(
                    last_line + "...",
                    max_width=max_width,
                    font=font
                )

                if len(last_line_components) == 1:
                    lines[-1] = last_line + "..."
                else:
                    last_line = last_line_components[0][:-3]
                    last_line += "..."
                    lines[-1] = last_line

                return FormatLocationResult(lines, font, line_height)
            else:
                return None

        except Exception as err:
            print(f"Error formatting location name: {err}")
            return None
