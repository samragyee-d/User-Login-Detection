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
                "description": data.get("description"),
                "country": data.get("country_code"),
                "owner_address": data.get("owner_address")
            }
        else:
            print(f"Error {response.status_code} for ASN {asn}")
    except Exception as e:
        print(f"Request failed for ASN {asn}: {e}")
    return None

if(isPrivateIP):
    get_asn_info(asn_df)