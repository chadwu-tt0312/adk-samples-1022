
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the Titanic dataset from the specified input directory

import pandas as pd

train_df = pd.read_csv('./input/train.csv')

# Preprocessing
# Drop columns that are not useful for prediction or require complex feature engineering for this simple example
# Keep 'Cabin' for feature extraction, but drop 'PassengerId', 'Name', 'Ticket'
train_df.drop(['PassengerId', 'Name', 'Ticket'], axis=1, inplace=True)

# Extract 'Deck' information from 'Cabin'
# Fill missing 'Cabin' values with 'Unknown' and then take the first letter
train_df['Deck'] = train_df['Cabin'].fillna('Unknown').astype(str).str[0]
# Drop the original 'Cabin' column as 'Deck' has been extracted
train_df.drop('Cabin', axis=1, inplace=True)

# Fill missing Embarked values with the mode
train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)

# Convert 'Sex' to numerical: 'male' to 0, 'female' to 1
train_df['Sex'] = train_df['Sex'].map({'male': 0, 'female': 1})

# Refine Age imputation strategy: fill missing 'Age' values with the median of their respective 'Pclass' and 'Sex' groups
train_df['Age'] = train_df.groupby(['Pclass', 'Sex'])['Age'].transform(lambda x: x.fillna(x.median()))

# One-hot encode 'Embarked', 'Pclass', and the new 'Deck' categorical features
# drop_first=True avoids multicollinearity, though not strictly necessary for simple models,
# it's good practice for tree-based models and general ML.
train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass', 'Deck'], drop_first=True)

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
