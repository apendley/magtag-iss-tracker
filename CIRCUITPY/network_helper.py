import os
import supervisor
import adafruit_connection_manager
import wifi
import socketpool
import adafruit_requests
import adafruit_ntp
from abbreviate_country import abbreviate_country

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

    def fetch_location_name(self, lat, lon):
        api_key = os.getenv("GEOAPIFY_KEY")
        url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api_key}&lang=en&limit=1"

        try:
            with self._requests.get(url) as response:
                json = response.json()
                _debug_print_geodata(json)

                if len(json["features"]) > 0:
                    feature = json["features"][0]
                    properties = feature["properties"]
                    return _location_name_from_properties(properties)

        except Exception as err:
            print(f"Failed to fetch geoapify data, error: {err}")


# Given a bag of properties, derive a location name.
def _location_name_from_properties(properties):
    # Aggregate location name components
    name_components = []

    # Component 1: city, district, or county
    if "city" in properties:
        print("Found city component")
        name_components.append(properties["city"])
    elif "district" in properties: 
        print("Found district component")
        name_components.append(properties["district"])        
    elif "county" in properties:
        print("Found county component")
        name_components.append(properties["county"])

    # Component 2: state or region
    if "state" in properties:
        print("Found state component")
        name_components.append(properties["state"])
    elif "region" in properties: 
        print("Found region component")
        name_components.append(properties["region"])        

    # Component 3: country
    if "country" in properties:
        print("Found country component")
        country_name = abbreviate_country(properties["country"])
        name_components.append(country_name)

    # Build the name from components, or use a fallback
    name = None

    # Did we find any name components?
    if len(name_components) > 0:
        # Assemble the name from the components we found in the properties
        name = ", ".join(name_components)
        print(f"Using location name from components: {name}")
    elif "formatted" in properties:
        # First fallback. We didn't start with this because it can return
        # street address level precision over land, which we don't really want.
        name = properties["formatted"]
        print(f"Using formatted location name: {name}") 
    elif "name" in properties:
        # Final fallback.
        name = properties["name"]
        print(f"Using default location name: {name}")

    # Finally, return the processed name, or nothing.
    return name

def _debug_print_geodata(json):
    # print(f"response headers:{response.headers}")
    # print(f"reverse geocode response: {json}")

    # Just print out the properties we care about, defined in this list.
    keys = ["city", "district", "county", "state", "region", "country", "formatted", "name"]

    print("    geodata:")
    if len(json["features"]) > 0:
        feature = json["features"][0]
        properties = feature["properties"]
    else:
        print("        no relevant geodata detected")
        return

    for key in keys:
        if key in properties:
            print(f"        {key}: {properties[key]}")    
