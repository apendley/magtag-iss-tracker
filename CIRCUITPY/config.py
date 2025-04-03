# How often in seconds to retrieve a new ISS position from the internet.
REFRESH_INTERVAL = 60

# The lifetime of a history marker in minutes.
# The ISS orbits once every ~90 minutes, so if you want the path to overlap
# with its previous orbit(s), make HISTORY_MARKER_DURATION ~90 or higher.
# Otherwise, use a value less than 90.
HISTORY_MARKER_DURATION = 80

# Home coordinate. Set this to wherever you are.
HOME_LATITUDE = 39.742043
HOME_LONGITUDE = -104.991531

# If True, distance is displayed in miles by default. Otherwise use km.
USE_MILES = True

# How close does the ISS need to be to home to turn the NeoPixels on?
# Value is in chosen units, e.g. miles if USE_MILES is True, otherwise km.
CLOSE_BY_DISTANCE = 1000

# What color should the boot/loading LEDs be?
LOADING_COLOR = 0xFFFF00

# What color should the busy LED be when fetching the ISS location?
FETCH_LOCATION_COLOR = 0x0000FF

# What color should the busy LED be when fetching geodata?
FETCH_GEODATA_COLOR = 0xFF00FF

# What color should the busy LED be when refreshing the display?
DISPLAY_REFRESH_COLOR = 0x00FF00

# What color should the nightlight be?
NIGHTLIGHT_COLOR = 0xFFFF30

# What color should the NeoPixels be when the ISS is close to home?
CLOSE_BY_COLOR = 0xFF0000

# Brightness levels.
LED_BRIGHTNESS_LEVELS = (0.05, 0.2, 0.4, 0.6, 0.8, 1.0)