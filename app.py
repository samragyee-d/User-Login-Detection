import pandas as pd
#import sklearn
import numpy as numpy

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split


df = pd.read_csv('rba-dataset.csv', nrows=1000)
print(df.head)
#First df = features 
#Second df = labels 
X_train, X_test, y_train, y_test = train_test_split(df[['IP Address', 'Country', 'User Agent String']], df['Is Attack IP'], test_size=.2)
bst = XGBClassifier(n_estimators=2, max_depth=2, learning_rate=1, objective='binary:logistic')


bst.fit(X_train, y_train)

preds = bst.predict(X_test)
