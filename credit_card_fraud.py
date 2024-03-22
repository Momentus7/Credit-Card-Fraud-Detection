# -*- coding: utf-8 -*-
"""Credit Card Fraud

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U6n4heFzxvrS2HHba62__Hg01pPz0OVQ
"""

import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV,train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import *

dt=pd.read_csv("/content/creditcardcodsoft.csv")

dt.head()

pd.options.display.max_columns=False

dt.info()

dt.isnull().sum()

dt=dt.dropna()

dt.info()

(dt[dt["Class"]==float(1)]["Class"].count()/dt["Class"].count())*100

(dt[dt["Class"]==float(0)]["Class"].count()/dt["Class"].count())*100

#the correlation matrix shows none of the features are collinear

corr_matrix = dt.drop(["Class"],axis=1).corr().abs().round(decimals=2)
print(corr_matrix)

import seaborn as sns
plt.figure(figsize=(22,20))
sns.heatmap(corr_matrix,annot=True)
plt.show()

dt.describe()

#check p value for all features to find the significant features

# import statsmodels.api as sm

# X = sm.add_constant(dt.drop(["Class"],axis=1))
# y=dt["Class"]

# logit_model = sm.Logit(y,X)
# result = logit_model.fit()

# summary = result.summary()
# print(summary)

xtrain, xval, ytrain, yval = train_test_split(dt.drop(["Class"], axis=1), dt["Class"], test_size=0.3, random_state=42)
xval, xtest, yval, ytest = train_test_split(xval, yval, test_size=0.5, random_state=42)

model = linear_model.LogisticRegression(max_iter=1000)

model.fit(xtrain, ytrain)

best_threshold = 0
best_recall = 0
best_precision = 0
best_f1score = 0

for threshold in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    y_pred_proba = model.predict_proba(xval)[:, 1]
    y_pred = (y_pred_proba > threshold).astype(int)
    recall = recall_score(yval, y_pred)
    precision = precision_score(yval, y_pred)
    f1 = f1_score(yval, y_pred)
    #since the dataset is biased use recall and precision
    #since detecting a fraud is more important than precision, recall should be given preference
    if recall > best_recall:
        best_recall = recall
        best_precision = precision
        best_f1score = f1
        best_threshold = threshold

print("Optimal Threshold:", best_threshold)
print("Recall:", best_recall)
print("Precision:", best_precision)
print("F1 Score:", best_f1score)

y_pred_test_proba = model.predict_proba(xtest)[:, 1]
y_pred_test = (y_pred_test_proba > best_threshold).astype(int)
recall_test = recall_score(ytest, y_pred_test)
precision_test = precision_score(ytest, y_pred_test)
f1_test = f1_score(ytest, y_pred_test)
print("\nEvaluation on Testing Set (using optimal threshold)")
print("Recall:", recall_test)
print("Precision:", precision_test)
print("F1 Score:", f1_test)

#increase the number of minority class samples (fraud cases)
from imblearn.over_sampling import SMOTE

smote=SMOTE()

x_new,y_new=smote.fit_resample(dt.drop(["Class"], axis=1),dt["Class"])

xtrain, xtest, ytrain, ytest = train_test_split(x_new, y_new, test_size=0.3, random_state=42)

model=linear_model.LogisticRegression(max_iter=1000)
model.fit(xtrain,ytrain)
y_pred=model.predict(xtest)
print("Recall is: ",recall_score(ytest,y_pred))
print("Precision is: ",precision_score(ytest,y_pred))
print("F1 Score is: ",f1_score(ytest,y_pred))

#decrease the number of majority class samples (non fraud cases)
# from imblearn.under_sampling import TomekLinks

# tomek_links = TomekLinks()

# x_new, y_new = tomek_links.fit_resample(dt.drop(["Class"], axis=1),dt["Class"])

# xtrain, xtest, ytrain, ytest = train_test_split(x_new, y_new, test_size=0.3, random_state=42)

# model=linear_model.LogisticRegression()
# model.fit(xtrain,ytrain)
# y_pred=model.predict(xtest)
# print("Recall is: ",recall_score(ytest,y_pred))
# print("Precision is: ",precision_score(ytest,y_pred))
# print("F1 Score is: ",f1_score(ytest,y_pred))

#logistic regression with best threshold=0.2 for recall with only significant features with small p values

new_df=dt[["V1","V4","V8","V9","V10","V13","V14","V20","V21","V22","V27","V28","Amount","Class"]]
xtrain,xtest,ytrain,ytest=train_test_split(new_df.drop(["Class"],axis=1),new_df["Class"],random_state=42)

model = linear_model.LogisticRegression(max_iter=1000)

model.fit(xtrain, ytrain)
y_pred_test_proba = model.predict_proba(xtest)[:, 1]
y_pred_test = (y_pred_test_proba > 0.2).astype(int)

print("Recall: ",recall_score(ytest,y_pred_test))
print("Precision is: ",precision_score(ytest,y_pred_test))
print("F1 Score is: ",f1_score(ytest,y_pred_test))

#RandomForestClassifier for various hyperparameters
param_grid = {
    'n_estimators': [25, 50, 100, 150],
    'max_features': ['sqrt', 'log2', None],
    'max_depth': [3, 6, 9],
    'max_leaf_nodes': [3, 6, 9],
}
grid_search = GridSearchCV(RandomForestClassifier(),
                           param_grid=param_grid,
                           cv=5)
grid_search.fit(xtrain,ytrain)
print(grid_search.best_estimator_)

#Chose the best hyperparameters
model_random = RandomForestClassifier(max_depth=6,
                                      max_features=None,
                                      max_leaf_nodes=6,
                                      n_estimators=25)
model_random.fit(xtrain, ytrain)
y_pred_rand = model_random.predict(xtest)
print(accuracy_score(y_pred_rand, ytest))