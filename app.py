import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split


df = pd.read_csv('rba-dataset.csv', nrows=1000)
df['Login Timestamp'] = pd.to_datetime(df['Login Timestamp'])




df['Country'] = df['Country'].astype('category')
df['User Agent String'] = df['User Agent String'].astype('category')
df['IP Address'] = df['IP Address'].astype('category')

X = df[['IP Address', 'Country', 'User Agent String']]
y = df['Is Attack IP']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


model = XGBClassifier(enable_categorical=True, n_estimators=2, max_depth=2, learning_rate=1, objective='binary:logistic')


model.fit(X_train, y_train)


preds = model.predict(X_test)

print(preds)
