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
    

# Filter for public IPs only
df_public = df[~df['IP Address'].apply(isPrivateIP)].copy()
df_public.reset_index(drop=True, inplace=True)

# API lookup function
def get_ip_info(ip):
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data["status"] == "success":
            return {
                "country": data["country"],
                "region": data["regionName"],
                "city": data["city"],
                "isp": data["isp"]
            }
        else:
            return {"country": "Error", "region": "", "city": "", "isp": data.get("message", "unknown")}
    except Exception as e:
        return {"country": "Error", "region": "", "city": "", "isp": str(e)}

# Query public IPs
results = []
for i, ip in enumerate(df_public['IP Address']):
    info = get_ip_info(ip)
    results.append(info)
    print(f"{i+1}/{len(df_public)} - {ip}: {info['country']}, {info['region']}, {info['city']}, {info['isp']}")
    time.sleep(1.4)  # throttle

# Add results to filtered DataFrame
df_public = pd.concat([df_public, pd.DataFrame(results)], axis=1)

# Save final result
#df_public.to_csv("public_ip_info_output.csv", index=False)