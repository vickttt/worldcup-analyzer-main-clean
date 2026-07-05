VENUE_CITY_FALLBACKS = {
    "MetLife Stadium": "East Rutherford, New Jersey, United States",
    "New York/New Jersey Stadium": "East Rutherford, New Jersey, United States",
    "Dallas Stadium": "Arlington, Texas, United States",
    "Los Angeles Stadium": "Inglewood, California, United States",
    "Miami Stadium": "Miami Gardens, Florida, United States",
    "Boston Stadium": "Foxborough, Massachusetts, United States",
    "Kansas City Stadium": "Kansas City, Missouri, United States",
    "Philadelphia Stadium": "Philadelphia, Pennsylvania, United States",
    "Houston Stadium": "Houston, Texas, United States",
    "Seattle Stadium": "Seattle, Washington, United States",
    "San Francisco Bay Area Stadium": "Santa Clara, California, United States",
    "Atlanta Stadium": "Atlanta, Georgia, United States",
    "Toronto Stadium": "Toronto, Canada",
    "Vancouver Stadium": "Vancouver, Canada",
    "BC Place Vancouver": "Vancouver, Canada",
    "Estadio Azteca": "Mexico City, Mexico",
    "Estadio Banorte": "Mexico City, Mexico",
    "Estadio Monterrey": "Monterrey, Mexico",
    "Estadio Guadalajara": "Guadalajara, Mexico",
}


def venue_city_for(venue_name, venue_city=None):
    city = str(venue_city or "").strip()
    if city:
        return city
    return VENUE_CITY_FALLBACKS.get(str(venue_name or "").strip(), "")
