from countryinfo import CountryInfo

country = CountryInfo('United States')
info = country.info()

# Latitude and longitude are in the 'latlng' key
latlng = info.get('latlng', [None, None])
print(latlng)  # Output: [latitude, longitude]
