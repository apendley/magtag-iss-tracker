from math import pi, radians, cos, sin, asin, sqrt

# Get the distance between two coordinates
def haversine(lat1, lon1, lat2, lon2, use_miles=True):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dLat = lat2 - lat1
    dLon = lon2 - lon1
 
    a = pow(sin(dLat / 2), 2) + pow(sin(dLon / 2), 2) * cos(lat1) * cos(lat2)
    c = 2 * asin(sqrt(a))

    # Radius of the earth
    r = 3958.8 if use_miles else 6371.0
    return r * c