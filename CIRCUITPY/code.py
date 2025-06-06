import board
import time
import os
import gc
import random
from math import ceil

import rtc
from adafruit_ticks import ticks_ms, ticks_diff

import displayio

from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.line import Line
import fonts

import config

###############
# Neopixels
###############
from neopixel import NeoPixel
neopixel = NeoPixel(board.NEOPIXEL, 4)

led_brightness_index = 0
neopixel.brightness = config.LED_BRIGHTNESS_LEVELS[led_brightness_index]

neopixel.fill(0)

###############
# I2C
###############
i2c = board.I2C()

##################
# Accelerometer
##################
import adafruit_lis3dh
accelerometer = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

##############################
# Display orientation
##############################
import display_orientation
from display_orientation import DisplayOrientation, LANDSCAPE_ALL

orientation = DisplayOrientation(allowed=LANDSCAPE_ALL)

###############
# Display
###############
display = board.DISPLAY
display.root_group = displayio.Group()

# Sync display rotation to accelerometer orientation
def sync_orientation():
    accel = accelerometer.acceleration
    display.rotation = orientation.sync(display.rotation, accel.x, accel.y)

# Coordinate display refresh with orientation handling.
def refresh_display(wait=True):
    # Sleep until we can refresh the display
    if wait == True and display.time_to_refresh > 0:
        time.sleep(display.time_to_refresh)

    # Sync the display with the accelerometer
    accel = accelerometer.acceleration
    display.rotation = orientation.sync(display.rotation, accel.x, accel.y)

    try:
        display.refresh()
    except Exception as err:
        print(err)

###############
# Layout
###############
from layout_helper import LayoutHelper
layout = LayoutHelper(display_width=display.width, display_height=display.height)

##################
# Splash screen
##################
SPLASH_IMAGES = [
    "assets/sprites/iss_01.bmp",
    "assets/sprites/iss_02.bmp",
    "assets/sprites/iss_03.bmp",
    "assets/sprites/iss_04.bmp",
    "assets/sprites/iss_05.bmp",
]

# Choose a random splash screen to start
current_splash_index = random.randrange(0, len(SPLASH_IMAGES))

# Used for splash led animation
splash_led_index = None

def render_splash_leds():
    global splash_led_index

    for i in range(0, 4):
        p = 3 - i if display.rotation == display_orientation.LANDSCAPE_TOP else i

        if i == splash_led_index:
            neopixel[p] = config.LOADING_COLOR
        else:
            neopixel[p] = 0x000000

def next_splash_led():
    global splash_led_index

    if splash_led_index == None:
        splash_led_index = 0
    else:
        splash_led_index += 1

        if splash_led_index >= 4:
            splash_led_index = 0

    render_splash_leds()

# Display the splash screen that corresponds to the current_splash_index
def show_splash():
    global current_splash_index

    group = displayio.Group()

    bg = Rect(0, 0, display.width, display.height, fill=0xFFFFFF)
    group.append(bg)

    iss_bitmap = displayio.OnDiskBitmap(SPLASH_IMAGES[current_splash_index])
    iss_sprite = displayio.TileGrid(iss_bitmap, pixel_shader=iss_bitmap.pixel_shader)
    iss_sprite_group = displayio.Group()
    iss_sprite_group.append(iss_sprite)
    iss_sprite_group.x = (display.width - iss_bitmap.width) // 2
    iss_sprite_group.y = (display.height - iss_bitmap.height) // 2

    group.append(iss_sprite_group)

    return group

# Display the next splash screen in the sequence, if the display is ready.
def next_splash():
    global current_splash_index

    next_splash_led()

    if display.time_to_refresh == 0:
        print("Showing next splash screen")

        # Choose a random splash screen that isn't the current one
        choices = range(0, len(SPLASH_IMAGES))
        choices = list(filter(lambda c: c != current_splash_index, choices))
        choice_index = random.randrange(0, len(choices))
        current_splash_index = choices[choice_index]

        # Show the new splash screen
        splash_group = show_splash()
        display.root_group = splash_group

        # No need to wait, we already know we can refresh.
        refresh_display(wait=False)
    else:
        print(f"next_splash(): Display is busy, time until refresh: {display.time_to_refresh}")

###################################
# Main program starts here
###################################

# Sync orientation for the first time
sync_orientation()

# Display initial splash screen
display.root_group = show_splash()
next_splash_led()
refresh_display()

###################################
# Connect to WiFi
###################################
from network_helper import Network
network = Network()
network.connect_to_wifi(on_retry=next_splash)

# Go to next splash screen, if we can
next_splash()

###################################
# Get current time
###################################
rtc.RTC().datetime = network.fetch_time(on_retry=next_splash)

# Go to next splash screen, if we can
next_splash()

###################################
# World map
###################################
map_bitmap = displayio.OnDiskBitmap("assets/sprites/worldmap-mono.bmp")
map_sprite = displayio.TileGrid(map_bitmap, pixel_shader=map_bitmap.pixel_shader)

world_map_group = displayio.Group()
world_map_group.x = layout.map_x_offset
world_map_group.append(map_sprite)

display.root_group = displayio.Group()
display.root_group.append(world_map_group)

# History markers
from history_marker import HistoryMarker

# Convert to milliseconds
HISTORY_MARKER_DURATION = config.HISTORY_MARKER_DURATION * 60 * 1000

# History marker storage
history_markers = []

# History marker rendering
history_markers_group = displayio.Group()
display.root_group.append(history_markers_group)

def add_history_marker(x, y):
    new_shape = Circle(x, y, layout.history_marker_radius, fill=0, stroke=0)
    history_markers.append(HistoryMarker(sprite=new_shape, time_to_live=HISTORY_MARKER_DURATION))
    history_markers_group.append(new_shape)

def update_history_markers(dt):
    removed_markers = []

    for marker_index in range(0, len(history_markers)):
        marker = history_markers[marker_index]

        marker.time_to_live -= dt

        if marker.time_to_live <= 0:
            # print(f"history marker is dead, removing")
            # history_markers_group.remove(marker.sprite)
            removed_markers.append(marker)
        else:
            # Decay linearly with time
            ratio = marker.time_to_live / HISTORY_MARKER_DURATION
            radius = ceil(ratio * layout.history_marker_radius)

            # If our radius has changed, replace the old sprite with a one with the new radius.
            if radius == 0:
                removed_markers.append(marker)
            elif marker.sprite.r != radius:
                new_sprite = Circle(marker.sprite.x0, marker.sprite.y0, radius, fill=0, stroke=0)
                marker.sprite = new_sprite
                history_markers_group.pop(marker_index)
                history_markers_group.insert(marker_index, new_sprite)

    for marker in removed_markers:
        history_markers_group.remove(marker.sprite)
        history_markers.remove(marker)

# Home icon
home_x, home_y = layout.lat_lon_to_screen(config.HOME_LATITUDE, config.HOME_LONGITUDE)

home_icon = Triangle(
    x0=home_x,
    y0=home_y - (layout.home_icon_radius - 1),
    x1=home_x + layout.home_icon_radius,
    y1=home_y + layout.home_icon_radius,
    x2=home_x - layout.home_icon_radius,
    y2=home_y + layout.home_icon_radius,
    fill=0xFFFFFF,
    outline=0x000000
)
display.root_group.append(home_icon)

# ISS Icon
iss_marker = Circle(0, 0, layout.iss_icon_radius, fill=0xFFFFFF, outline=0, stroke=2)
iss_marker.hidden = True
display.root_group.append(iss_marker)

# Info panel
info_panel_bg = Rect(0, 0, layout.map_x_offset, display.height, fill=0xFFFFFF)
display.root_group.append(info_panel_bg)

# Overlap the map slightly to give the location text a little more breathing room.
info_panel_separator = Rect(layout.info_panel_content_width + 2, 0, 2, display.height, fill=0x808080)
display.root_group.append(info_panel_separator)

# Distance label background
distance_bg = Rect(0, 0, layout.map_x_offset, layout.distance_bg_height, fill=0x808080) 
display.root_group.append(distance_bg)

# Distance label
distance_label = Label(
    font=fonts.NUMERIC_32, 
    text="",
    anchor_point = (0.5, 0.5),
    color=0
)
distance_label.anchored_position = (layout.distance_label_x_center, layout.distance_label_y_center)
display.root_group.append(distance_label)

def set_distance_text(dist):
    distance_text = f"{dist}"
    distance_label.font = layout.font_for_distance_text(distance_text)
    distance_label.text = distance_text

# Distance units label
distance_units_label = Label(
    font=fonts.REGULAR_12,
    text=layout.units_text(config.USE_MILES),
    anchor_point = (0.5, 0.0),
    color=0
)
distance_units_label.anchored_position = (layout.distance_label_x_center, layout.distance_units_y_offset)
display.root_group.append(distance_units_label)

# Location label group
location_label_group = displayio.Group()
location_label_group.x = layout.text_left_margin
location_label_group.y = layout.location_name_y_offset
display.root_group.append(location_label_group)

# Last updated label
timestamp_label = Label(
    font=fonts.REGULAR_8,
    text="",
    anchor_point=(1.0, 1.0),
    color=0x000000,
    background_color = 0xFFFFFF
)
timestamp_label.anchored_position = (layout.display_width, layout.display_height)
display.root_group.append(timestamp_label)

# Set formatted location text
def set_location_text(text):
    n = len(location_label_group)
    for i in range(0, n):
        location_label_group.pop()

    if text is None or text == "":
        return

    layout_result = layout.layout_location_name(text)
    
    if layout_result is None:
        # Should probably throw but oh well
        return

    print("rendered text:")

    y = 0
    for line in layout_result.lines:
        print(f"    {line}")

        label = Label(
            font=layout_result.font,
            text=line,
            color=0
        )

        label.y = y
        y += layout_result.line_height

        location_label_group.append(label)

# Update map with new ISS coordinates
def update_map(lat, lon):
    global history_markers_group, iss_marker

    # Update the current position marker
    iss_x, iss_y = layout.lat_lon_to_screen(lat, lon)
    iss_marker.x0 = iss_x
    iss_marker.y0 = iss_y
    iss_marker.hidden = False

    # Add a new history marker at the current position
    add_history_marker(iss_x, iss_y)

    # Update timestamp label not now
    now = time.localtime()
    timestamp_label.text = f"{now.tm_mon:02}/{now.tm_mday:02} {now.tm_hour:02}:{now.tm_min:02}:{now.tm_sec:02} UTC"

##################
# Buttons
##################
import digitalio
from adafruit_debouncer import Debouncer

# BOOT0 is used as a brightness cycle
button_pins = [board.BUTTON_A, board.BUTTON_B, board.BUTTON_C, board.BUTTON_D, board.BOOT0]
buttons = []

for b in range(0, len(button_pins)):
    pin = digitalio.DigitalInOut(button_pins[b])
    pin.direction = digitalio.Direction.INPUT
    pin.pull = digitalio.Pull.UP
    buttons.append(Debouncer(pin))

def update_buttons():
    for button in buttons:
        button.update()

##################
# LEDs
##################
night_light_on = False
is_close_to_home = False

# True if a night light toggle button was just pressed.
# The right-most 3 buttons toggle the night light
def night_light_toggled():
    if display.rotation == display_orientation.LANDSCAPE_TOP:
        button_indices = range(1, 4)
    else:
        button_indices = range(0, 3)

    for index in button_indices:
        if buttons[index].fell:
            return True

    return False

# True if distance unit toggle button was pressed.
# The left-most button toggles the units between miles/km
def distance_units_toggled():
    if display.rotation == display_orientation.LANDSCAPE_TOP:
        button_index = 0
    else:
        button_index = 3

    if buttons[button_index].fell:
        return True

    return False

# True if the brightness button was just pressed.
def brightness_cycled():
    return buttons[4].fell

# Busy LED is the left-most LED, depending on orientation.
def set_busy_led_color(color):
    if display.rotation == display_orientation.LANDSCAPE_TOP:
        neopixel[3] = color
    else:
        neopixel[0] = color

def update_leds():
    global night_light_on, is_close_to_home

    if is_close_to_home:
        resting_color = config.CLOSE_BY_COLOR
    elif night_light_on:
        resting_color = config.NIGHTLIGHT_COLOR
    else:
        resting_color = 0x000000

    neopixel.fill(resting_color)

#############################
# State tracking
#############################
import supervisor

# Update interval tracking
last_refresh_time = 0

# Occasionally, it seems like requests start to fail after the device has been running for awhile,
# and they never succeed again after that. Everything works again after a reboot and re-connection.
# Thus, as a workaround, if we notice too many failures in a row, soft reboot the device.
# Not ideal, but unless/until I find a proper fix, it's better than just sitting there
# for hours failing and waiting for a manual reboot.
consecutive_refresh_failures = 0

def on_refresh_coordinate(succeeded):
    global consecutive_refresh_failures    

    if succeeded:
        consecutive_refresh_failures = 0
    else:
        consecutive_refresh_failures += 1

        if consecutive_refresh_failures >= 5:
            print("Too many consecutive coordinate refresh failures, reloading...")
            supervisor.reload()

# Track whether currently displaying miles or km.
# Initialize to whatever the user has decided for the default.
is_displaying_miles = config.USE_MILES

# Distance to home
distance_in_miles = 100000

def distance_in_km():
    global distance_in_miles
    return distance_in_miles * 1.60934

# Get distance to home in whatever units we're currently displaying
def get_distance_to_home():
    global distance_in_miles, is_displaying_miles
    return int(distance_in_miles if is_displaying_miles else distance_in_km())    

# Return "close-by" distance, based on display units and default units.
def get_close_by_distance():
    global is_displaying_miles

    if is_displaying_miles:
        if not config.USE_MILES:
            return config.CLOSE_BY_DISTANCE * 1.60934
    else:
        if config.USE_MILES:
            return config.CLOSE_BY_DISTANCE / 1.60934    

    return config.CLOSE_BY_DISTANCE        

# Turn off all LEDs
neopixel.fill(0x000000)

# Final imports needed for main loop
from haversine import haversine

####################
# Main loop
####################
while True:
    # If this is True by the end of the loop, the display will be refreshed.
    display_needs_refresh = False

    # Refresh data when it's time. This is a blocking call, so we the status LED to indicate that we're busy.
    last_refreshed_dt = ticks_diff(ticks_ms(), last_refresh_time)

    if last_refresh_time == 0 or last_refreshed_dt >= config.REFRESH_INTERVAL * 1000:
        gc.collect()
        print(f"\n--- Free memory: {gc.mem_free()} ---")

        print("Fetching latest ISS coordinate")
        set_busy_led_color(config.FETCH_LOCATION_COLOR)
        coordinate = network.fetch_iss_coordinate()

        # Track if we succeeded fetching the coordinate or not.
        on_refresh_coordinate(succeeded=(coordinate is not None))

        if coordinate is not None:
            # Since the network requests are blocking, track the time it takes for them to complete,
            # so we can apply that time to our history markers decay rate; otherwise, it won't be accounted for.
            requests_start_time = ticks_ms()

            # unpack coordinate
            lat, lon = coordinate[0], coordinate[1]
            print(f"    ISS coordinate: {lat}, {lon}")

            # Get distance to home using the Haversine formula.
            distance_in_miles = haversine(lat, lon, config.HOME_LATITUDE, config.HOME_LONGITUDE, use_miles=True)

            # Get our distance to home and our close-by distance.
            distance_to_home = get_distance_to_home()
            close_by_distance = get_close_by_distance()

            # Update distance label
            set_distance_text(distance_to_home)

            # Flag whether we're close to home or not.
            is_close_to_home = distance_to_home <= close_by_distance
            
            # Get updated location name
            print("Fetching geodata for coordinate")
            set_busy_led_color(config.FETCH_GEODATA_COLOR)

            # Fetch geodata and get location name
            geodata = network.fetch_geodata(lat, lon)
            location_name = layout.location_name_from_geodata(geodata)
            set_location_text(location_name)

            # Update map
            update_map(lat, lon)

            # Make history markers size decay with time
            decay_dt = last_refreshed_dt + ticks_diff(ticks_ms(), requests_start_time)
            update_history_markers(last_refreshed_dt)

            # Need to refresh the display
            display_needs_refresh = True

        # Reset data refresh timer
        last_refresh_time = ticks_ms()

    # Update buttons
    update_buttons()

    # Update brightness
    if brightness_cycled():
        led_brightness_index += 1

        if led_brightness_index >= len(config.LED_BRIGHTNESS_LEVELS):
            led_brightness_index = 0

        neopixel.brightness = config.LED_BRIGHTNESS_LEVELS[led_brightness_index]

    # Update night light toggle
    if night_light_toggled():
        night_light_on = not night_light_on

    # Update distance units toggle
    if distance_units_toggled():
        is_displaying_miles = not is_displaying_miles
        distance_label.text = f"{get_distance_to_home()}"
        distance_units_label.text = layout.units_text(is_displaying_miles)        
        display_needs_refresh = True

    # Update orientation if necessary
    accel = accelerometer.acceleration
    orientation_dirty = display.rotation != orientation.sync(display.rotation, accel.x, accel.y)

    if display_needs_refresh or orientation_dirty:
        set_busy_led_color(config.DISPLAY_REFRESH_COLOR)
        refresh_display()

    # Update LEDs
    update_leds()
