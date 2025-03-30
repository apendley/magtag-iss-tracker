# How often in seconds to retrieve a new ISS position from the internet.
REFRESH_INTERVAL = 60

# How many previous ISS locations to display in the trail.
# The longer your refresh interval is, the shorter you'll probably want this to be.
MAX_LOCATION_HISTORY = 75

# Home coordinate. Set this to wherever you are.
HOME_LATITUDE = 39.742043
HOME_LONGITUDE = -104.991531

# If True, distance is displayed in miles by default. Otherwise use km.
USE_MILES = True

# How close does the ISS need to be to home to turn the NeoPixels on?
# Value is in chosen units, e.g. miles if USE_MILES is True, otherwise km.
CLOSE_BY_DISTANCE = 1000

# What color should the boot/loading LEDs be?
LOADING_COLOR = 0x404000

# What color should the busy LED be when fetching the ISS location?
FETCH_LOCATION_COLOR = 0x000040

# What color should the busy LED be when fetching geodata?
FETCH_GEODATA_COLOR = 0x400040

# What color should the busy LED be when refreshing the display?
DISPLAY_REFRESH_COLOR = 0x003000

# What color should the nightlight be?
NIGHTLIGHT_COLOR = 0xFFFF30

# What color should the NeoPixels be when the ISS is close to home?
CLOSE_BY_COLOR = 0xFF0000

# Overall LED brightness (0.0 to 1.0)
LED_BRIGHTNESS = 0.05