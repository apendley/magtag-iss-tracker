
# I don't actually know if all of these will be seen but if they
# are they save a ton of space in the UI, and take relatively
# little RAM since we've got the MagTag's PSRAM.
ABBREVIATED_COUNTRY_NAMES = {
    "United States": "USA",
    "United Arab Emirates": "UAE",
    "United Kingdom": "UK",
    "Republic of the Congo": "Congo",
    "Democratic Republic of the Congo": "Congo",
    'Central African Republic': 'C African Rep',
    'Saint Vincent and the Grenadines': 'St Vincent & Grenadines',
    'São Tomé and Príncipe': 'Sao Tome & Principe',
    'Trinidad and Tobago': 'Trinidad & Tobago',
    'Saint Kitts and Nevis': 'St Kitts & Nevis',
    'Saint Lucia': 'St Lucia',
    'Bosnia and Herzegovina': 'Bosnia Herzegovina',
    'Antigua and Barbuda': 'Antigua & Barbuda',
    'Republic of the Congo': 'Congo',
    "Republic of Korea": "South Korea",
    "Bolivarian Republic of Venezuela": "Venezuela",
    "People's Republic of China": "China",
    "Republic of South Africa": "South Africa",
    "Federal Republic of Brazil": "Brazil",
    "Republic of India": "India",
    "Federal Republic of Germany": "Germany",
    "Islamic Republic of Iran": "Iran",
}

def abbreviate_country(name):
    return ABBREVIATED_COUNTRY_NAMES.get(name, name)
