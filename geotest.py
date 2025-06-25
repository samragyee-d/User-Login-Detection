from geopy.geocoders import Nominatim
import pandas as pd
import time

df = pd.read_csv('rba-dataset.csv', nrows=1000)

geocollector = Nominatim(user_agent='geocoder')

def geocode_address(row):
    try:
        location = geocollector.geocode(f"{row['Country']}", timeout=10)
        time.sleep(1)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Could not geocode: {row['Country']}")
            return None, None
    except Exception as e:
        print(f"Error geocoding {row['Country']}: {e}")
        return None, None

df['Latitude'], df['Longitude'] = zip(*df.apply(geocode_address, axis=1))

print(df[['Country', 'Latitude', 'Longitude']])
