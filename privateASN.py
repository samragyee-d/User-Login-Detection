import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import ipaddress
import requests
import time

#defining dataset
df = pd.read_csv('rba-dataset.csv', nrows=1000)

#defining main column
column_a = df['User ID']

#setting up IP conversion variables:
classA = '10.0.0.0/8'
classB = '172.16.0.0/12'
classC = '192.168.0.0/16'

private_networks = [
    ipaddress.IPv4Network('10.0.0.0/8'),
    ipaddress.IPv4Network('172.16.0.0/12'),
    ipaddress.IPv4Network('192.168.0.0/16')
]

networkA = ipaddress.IPv4Network(classA)
networkB = ipaddress.IPv4Network(classB)
networkC = ipaddress.IPv4Network(classC)

privateIP = ''
publicIP = ' '


#iterating throw user logs
for i, row in df.iterrows():
    ip_str = row['IP Address']
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj in networkA or ip_obj in networkB or ip_obj in networkC:
            privateIP = ip_obj
        else:
            publicIP = ip_obj
    except ValueError:
        print(f"{ip_str} is invalid")

def isPrivateIP(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return any(ip_obj in net for net in private_networks)
    except ValueError:
        return True

asn_df = df = df[['ASN']]
    
def get_asn_info(asn):
    url = f"https://api.bgpview.io/asn/{asn}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()['data']
            return {
                "asn": data["asn"],
                "name": data.get("name"),
                "country": data.get("country_code"),
                "owner_address": data.get("owner_address")
            }
        else:
            print(f"Error {response.status_code} for ASN {asn}")
    except Exception as e:
        print(f"Request failed for ASN {asn}: {e}")
    return None


asn_info_list = []
unique_asns = asn_df['ASN'].dropna()

asn_info_list = []

if(isPrivateIP):
    get_asn_info(asn_df)


def geocode_address(address_list):
    # Step 1: Clean and format full address
    cleaned = list(dict.fromkeys([a.strip().title() for a in address_list if a.strip()]))
    full_address = ', '.join(cleaned)

    def query_nominatim(q):
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': q, 'format': 'json', 'limit': 1}
        headers = {'User-Agent': 'ASN-Geocoder/1.0'}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
        except Exception as e:
            print(f"Geocoding error for '{q}': {e}")
        return None

    # Try full address first
    coords = query_nominatim(full_address)
    if coords:
        return coords

    # Step 2: Retry with simplified fallback (city + country)
    city = None
    country = None
    for part in reversed(cleaned):
        if part.isalpha() and len(part) >= 3:
            if not country:
                country = part
            elif not city:
                city = part
                break
    fallback = ', '.join(filter(None, [city, country]))
    if fallback:
        print(f"Retrying with fallback address: {fallback}")
        coords = query_nominatim(fallback)
        if coords:
            return coords

    print(f"Geocoding failed for: {full_address}")
    return {"lat": None, "lon": None}


    

for asn in unique_asns:
    try:
        asn = int(asn)
        info = get_asn_info(asn)
        if info:
            coords = geocode_address(info['owner_address'])
            info.update(coords)
            asn_info_list.append(info)
            print(info)
        time.sleep(1.5)  # be nice to both APIs
    except ValueError:
        print(f"Invalid ASN: {asn}")