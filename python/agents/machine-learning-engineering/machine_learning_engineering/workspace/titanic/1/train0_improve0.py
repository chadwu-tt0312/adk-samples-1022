
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the Titanic dataset from the specified input directory

import pandas as pd
import re

train_df = pd.read_csv('./input/train.csv')

# --- New Feature Engineering ---

# 1. Extract titles from 'Name'
train_df['Title'] = train_df['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)

# Map some titles to more common ones
train_df['Title'] = train_df['Title'].replace(['Mlle', 'Ms'], 'Miss')
train_df['Title'] = train_df['Title'].replace('Mme', 'Mrs')

# Group rare titles into a single category
# List of titles to be considered 'Rare' after standardization
rare_titles = ['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona']
train_df['Title'] = train_df['Title'].replace(rare_titles, 'Rare')

# 2. Create 'FamilySize' feature by summing 'SibSp' and 'Parch'
# Adding 1 to include the passenger themselves
train_df['FamilySize'] = train_df['SibSp'] + train_df['Parch'] + 1

# Preprocessing
# Drop columns that are not useful for prediction or require complex feature engineering for this simple example
# 'Name' is dropped after its title information has been extracted.
train_df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

# Fill missing Age values with the median
train_df['Age'].fillna(train_df['Age'].median(), inplace=True)

# Fill missing Embarked values with the mode
train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)

# Convert 'Sex' to numerical: 'male' to 0, 'female' to 1
train_df['Sex'] = train_df['Sex'].map({'male': 0, 'female': 1})

# One-hot encode 'Embarked', 'Pclass', and the new 'Title' categorical features
# drop_first=True avoids multicollinearity, though not strictly necessary for simple models,
# it's good practice for tree-based models and general ML.
train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass', 'Title'], drop_first=True)

# Define features (X) and target (y)
X = train_df.drop('Survived', axis=1)
y = train_df['Survived']


# Split data into training and validation sets
# A test_size of 0.2 means 20% of the data will be used for validation
# random_state ensures reproducibility of the split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the XGBoost Classifier
# objective='binary:logistic' for binary classification (survival prediction)
# eval_metric='logloss' is a common metric for binary classification problems in XGBoost
# use_label_encoder=False suppresses a future deprecation warning
# random_state for reproducibility
xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)

# Train the XGBoost model on the training data
xgb_clf.fit(X_train, y_train)

# Make predictions on the validation set
y_pred_xgb = xgb_clf.predict(X_val)

# Evaluate accuracy on the validation set
# Accuracy is a suitable metric for this balanced binary classification task
accuracy_xgb = accuracy_score(y_val, y_pred_xgb)

# Print the final validation performance in the required format
print(f"Final Validation Performance: {accuracy_xgb:.4f}")
