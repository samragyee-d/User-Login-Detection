import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import ipaddress

#defining dataset
df = pd.read_csv('rba-dataset.csv', nrows=1000)

#defining main column
column_a = df['User ID']



#setting up IP conversion variables:
classA = '10.0.0.0/8'
classB = '172.16.0.0/12'
classC = '192.168.0.0/16'

networkA = ipaddress.IPv4Network(classA)
networkB = ipaddress.IPv4Network(classB)
networkC = ipaddress.IPv4Network(classC)


#iterating throw user logs
for value in column_a:
    timestamps = df['Login Timestamp']
    IPAddress = df['IP Address']
    IPAddress = ipaddress.ip_address(IPAddress)
    if IPAddress in networkA or IPAddress in networkA or IPAddress in networkA:
        print(f"{IPAddress} is in public")
else:
    print(f"{IPAddress} is private")
    
    #print(timestamps, IPAddress)
    