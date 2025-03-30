# For the MagTag, the orientation is defined by the position of the NeoPixels 
# in relation to the screen in a given rotation.
# e.g.:
#   * in PORTRAIT_LEFT, the NeoPixels will be to the left of the display.
#   * in LANDSCAPE_TOP, the NeoPixels will be above the display.

PORTRAIT_LEFT = 0
LANDSCAPE_BOTTOM = 90
PORTRAIT_RIGHT = 180
LANDSCAPE_TOP = 270

ALL = {PORTRAIT_LEFT, LANDSCAPE_BOTTOM, PORTRAIT_RIGHT, LANDSCAPE_TOP}
LANDSCAPE_ALL =  {LANDSCAPE_BOTTOM, LANDSCAPE_TOP}
PORTRAIT_ALL = {PORTRAIT_LEFT, PORTRAIT_RIGHT}

# Require the accelerometer force to at least be this so we don't get spurious
# orientation changes when the device is flat or mostly-flat.
ORIENTATION_CHANGE_MAGNITUDE_MIN = 3

def is_landscape(rotation):
    return rotation == PORTRAIT_RIGHT or rotation == PORTRAIT_LEFT

def is_portrait(rotation):
    return not is_landscape(rotation)

class DisplayOrientation:
    # Allowed should be a set of the allowed orientations.
    def __init__(self, allowed=ALL):
        self._allowed = allowed

    @property
    def allowed(self):
        return self._allowed

    def sync(self, current_rotation, accel_x, accel_y):
        rotation = self._rotation_from_acceleration(accel_x, accel_y)

        if (rotation is not None) and (rotation != current_rotation) and (rotation in self._allowed):
            return rotation

        return current_rotation

    def _rotation_from_acceleration(self, accel_x, accel_y):
        # Square both sides of the equation to avoid sqrt operation
        if (accel_x**2 + accel_y**2) < (ORIENTATION_CHANGE_MAGNITUDE_MIN ** ORIENTATION_CHANGE_MAGNITUDE_MIN):
            return None

        if abs(accel_x) > abs(accel_y):
            return PORTRAIT_RIGHT if accel_x > 0 else PORTRAIT_LEFT
        else:
            return LANDSCAPE_TOP if accel_y > 0 else LANDSCAPE_BOTTOM
