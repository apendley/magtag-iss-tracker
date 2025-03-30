# magtag-iss-tracker
An International Space Station tracker for the [Adafruit MagTag](https://www.adafruit.com/product/4800) written in CircuitPython 9. Tracks the location of the ISS in relation to the Earth, and provides information about each location.

![MagTag running ISS Tracker firmware](https://github.com/apendley/magtag-iss-tracker/blob/main/hero.jpeg)

Inspired by and based on [Simon Prickett's Badger ISS Tracker](https://github.com/simonprickett/iss-tracker) project, including use of ideas, code, and assets.

## Features
* Easily customizable by plugging MagTag into a computer and editing secrets and config files
* Uses free APIs provided by OpenNotify and Geoapify to provide location data (API key required for Geoapify data)
  * When possible, displays city/count/district, state/region, and country information for current location.
  * Displays names of bodies of water. Handy, since they make up most of the surface area of the planet!
* Geofence alert: Tracks distance of the ISS from a "home" location, and lights up LEDs when within range (customizable in config)
* Switch between miles and kilometers for distance display with the press of a button
* Night Light mode: Toggle LEDs on/off to use the MagTag as a simple night light
* Display auto-rotates based on accelerometer, easily allowing usage in standard and "upside down" orientations.
* Blinkenlights!

### Notes
* An API key is required from Geoapify in order to download location metadata. Accounts are free, and the API is free to use up to 3k requests a day, and 90k requests a month, which is more than plenty if with the default refresh duration.
* CircuitPython's network requests are blocking. Most of the time this won't matter, but it does mean that button presses will be ignored while fetching data from the internet. The left-most LED behaves as a status indicator; when it's not blue, purple, or green (configurable), button presses will be accepted.
* CircuitPython's text wrapping functions don't seem to count dashes as natural breaking points. Some mitigations are taken, such as trying to prevent line breaks on long words, but short of fixing this at the source I'm not sure how to eliminate the problem entirely.

# Installation
Before we begin installation, you'll need a Geoapify API key. If you don't have one, you can sign up for an account and get one for free at [https://myprojects.geoapify.com/register]. Then, follow the steps below to generate an API key:
1. Once logged in to Geoapify, go to the [projects page](https://myprojects.geoapify.com/projects)
2. Click "Add a new project", and enter a project name. I named mine "ISS Tracker"
3. Click on the project you just created
4. Your API key can be found here. You'll need this later after installing the firmware onto your MagTag.

1. Install CircuitPython 9 on your MagTag. As of this writing, the current version is 9.2.6. You can find 9CircuitPython installation instruction for the MagTag here](https://learn.adafruit.com/adafruit-magtag/circuitpython).
2. Delete all files from your MagTag's CIRCUITPY drive.
3. Download or clone this repo.
4. Copy the contents of the CIRCUITPY from the downloaded/cloned repo to your MagTag's CIRCUITPY drive.
5. Open the **settings.toml** file on your MagTag's CIRCUITPY drive in your favorite text editor.
6. Replace SSID with your WiFi network's SSID
7. Replace PASSWORD with your WiFi network's password
8. Replace KEY with your Geoapify API key you created earlier.
9. Save and close file.

That's it! If you're okay with the default configuration, you're good to go. If you'd like to cusomize the settings, such as the location refresh rate, home location, etc, open the config.py file on the MagTag's CIRCUITPY drive in your favorite text editor, and modify any settings you wish.

WARNING: It is probably not a good idea to refresh the location more often than once per minute. Doing so may cause the tracker to hit the Geoapify rate limit. 

# Usage
## Booting
Once the firmware is copied to your MagTag, and you've entered your network settings and API key, you can unplug the MagTag from your computer if you wish. If you want to change any of the settings in the future, simply turn the power toggle switch on the MagTag to the "off" position, plug it into your computer, toggle the power on, and edit the settings.toml and/or config.py files.

Once the MagTag is powered on, the ISS tracker firmware will try to connect to the WiFi network. If the settings were entered correctly, it should connect in anywhere betwen a few to 15-20 seconds. During this time, the MagTag will display a slide show of a few selected images relating to the International Space Station, and animate the LEDs. Once connected, the tracker will download the ISS location information for the first time and display the map screen.

## Display rotation
The display will automatically adjust to either the default landscape orientation, or the "upside down" landscape orientation.

## Status Indicator LED
Whichever orientation you choose, the left-most LED will behave as a status indicator. When this indicator is lit, button input cannot be processed. The indicator may light up in one of 3 colors, depending on the state:
* Fetching ISS coordinate: The status LED will glow blue (unless customized) when download the ISS coordinate.
* Fetching location metadata: The status LED will glow purple (unless customized) when downloading the corresponding location metadata.
* Refreshing the screen: The status LED will glow green (unless customized) when refreshing the screen.

## Toggle Miles/Kilometers
Once in the map screen, press the left-most button to toggle between miles/kilometers The status LED will glow green to indicate the screen is refreshing.

## Toggle Night Light mode
Once in the map screen, press any of the 3 right-most buttons to toggle night light mode on/off.

# Limitations
This project only works on WiFi networks with SSID and password. It is unlikely to work on public WiFi networks that use captive portals for signup or accepting terms and conditions.


# Action shots
You can find some images and videos from the following posts from my Bluesky account.

* [Boot Slide show](https://bsky.app/profile/did:plc:vzyhuqgujb6qhl5mrpudqda2/post/3llmjf6fcfc2j)
* [Proximity alert](https://bsky.app/profile/did:plc:vzyhuqgujb6qhl5mrpudqda2/post/3llmjx36rec2j)
* [Miles/Kilometers toggle](https://bsky.app/profile/did:plc:vzyhuqgujb6qhl5mrpudqda2/post/3llmjz2h5n22j)
* [Night light toggle](https://bsky.app/profile/did:plc:vzyhuqgujb6qhl5mrpudqda2/post/3llmkbouej22j)
