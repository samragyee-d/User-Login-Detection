import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


df = pd.read_csv('rba-dataset.csv', nrows=1000)

column_a = df['User ID']

for value in column_a:
    timestamps = df['Login Timestamp']
    IPAddress = df['IP Address']
    print(timestamps, IPAddress)