import pandas as pd
df = pd.read_csv("rba-dataset.csv", nrows=20000)
df_unique = df['User ID'].value_counts()
print(df_unique)