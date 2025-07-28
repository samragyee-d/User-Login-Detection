import pandas as pd
import ipaddress
import requests
import time

# Load dataset
df = pd.read_csv('rba-dataset.csv', nrows=1000)
print(df.head())  # Optional, remove if you want no prints

# IP private networks
private_networks = [
    ipaddress.IPv4Network('10.0.0.0/8'),
    ipaddress.IPv4Network('172.16.0.0/12'),
    ipaddress.IPv4Network('192.168.0.0/16')
]

def isPrivateIP(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return any(ip_obj in net for net in private_networks)
    except ValueError:
        return True  # treat invalid IPs as private (or you can change this)

# Extract ASN column for processing (do NOT overwrite df)
asn_df = df[['ASN']].copy()

# Get unique ASN values skipping NaN
unique_asns = asn_df['ASN'].dropna().unique()

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

def geocode_address(address_list):
    # Clean and format address
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

    coords = query_nominatim(full_address)
    if coords:
        return coords

    # Fallback: try city and country only
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

# Collect ASN info with lat/lon
asn_info_list = []
for asn in unique_asns:
    try:
        asn = int(asn)
        info = get_asn_info(asn)
        if info:
            coords = geocode_address(info['owner_address'] if info['owner_address'] else [])
            info.update(coords)
            asn_info_list.append(info)
            #print(info)
        time.sleep(1.5)  # avoid API rate limits
    except ValueError:
        print(f"Invalid ASN: {asn}")

# Convert to DataFrame and save to CSV
asn_info_df = pd.DataFrame(asn_info_list)
asn_info_df.to_csv("asn_info_with_lat_lon.csv", index=False)
