import os
import supervisor
import adafruit_connection_manager
import wifi
import socketpool
import adafruit_requests
import adafruit_ntp
from collections import namedtuple

GeoData = namedtuple("GeoData", [
    "city",
    "district",
    "county",
    "state",
    "region",
    "country",
    "name"
])

class Network:
    def __init__(self):
        self._pool = None
        self._requests = None

    def connect_to_wifi(self, on_retry=None):
        wifi_ssid = os.getenv("WIFI_SSID")
        wifi_password = os.getenv("WIFI_PASSWORD")

        if wifi_ssid is None:
            print("WiFi credentials are kept in settings.toml, please add them there!")
            raise ValueError("SSID not found in environment variables")

        connection_attempts = 1
        MAX_CONNECTION_ATTEMPTS = 20

        for i in range(0, MAX_CONNECTION_ATTEMPTS):
            print(f"\nConnecting to WiFi, attempt {connection_attempts}")

            try:
                wifi.radio.connect(wifi_ssid, wifi_password)
                break
            except ConnectionError as err:
                connection_attempts += 1

                if connection_attempts > MAX_CONNECTION_ATTEMPTS:
                    print(f"Failed to connect to WiFi with provided credentials, error: {err}.\nNo attempts remaining. Soft-rebooting.")
                    supervisor.reload()
                else:
                    print(f"Failed to connect to WiFi with provided credentials, error: {err}.\nRetrying...")

                    if on_retry is not None:
                        on_retry()

        self._pool = socketpool.SocketPool(wifi.radio)
        ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
        self._requests = adafruit_requests.Session(self._pool, ssl_context)
        print("Connected to WiFi")  

    def fetch_time(self, on_retry=None):
        while True:
            try:
                print("Fetching current time")
                ntp = adafruit_ntp.NTP(self._pool, tz_offset=0, cache_seconds=3600)
                return ntp.datetime
            except Exception as err:
                print(f"Error getting time: {err}")

                if on_retry is not None:
                    on_retry()

    def fetch_iss_coordinate(self):
        try:
            with self._requests.get("http://api.open-notify.org/iss-now.json") as response:
                json = response.json()
                location = json["iss_position"]

                lat = float(location["latitude"])
                lon = float(location["longitude"])

                return (lat, lon)

        except Exception as err:
            print(f"Failed to fetch ISS location, error: {err}")

        return None

    def fetch_geodata(self, lat, lon):
        api_key = os.getenv("GEOAPIFY_KEY")
        url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api_key}&lang=en&limit=1"

        try:
            with self._requests.get(url) as response:
                json = response.json()

                if len(json["features"]) > 0:
                    feature = json["features"][0]
                    properties = feature["properties"]
                    _debug_print_geodata(properties)
                    return _geodata_from_properties(properties)

        except Exception as err:
            print(f"Failed to fetch geoapify data, error: {err}")

        return None

# Given a bag of properties, derive a location name.
def _geodata_from_properties(properties):
    formatted = properties["formatted"] if "formatted" in properties else None
    name = properties["name"] if "name" in properties else None    

    return GeoData(
        city=properties["city"] if "city" in properties else None,
        district=properties["district"] if "district" in properties else None,
        county=properties["county"] if "county" in properties else None,
        state=properties["state"] if "state" in properties else None,
        region=properties["region"] if "region" in properties else None,
        country=properties["country"] if "country" in properties else None,
        name=formatted if formatted is not None else name
    )

# Print the properties we care about from returned geodata properties
def _debug_print_geodata(properties):
    # Just print out the properties we care about, defined in this list.
    keys = ["city", "district", "county", "state", "region", "country", "formatted", "name"]

    for key in keys:
        if key in properties:
            print(f"    {key}: {properties[key]}")    

