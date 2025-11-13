
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb  # Import LightGBM
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the Titanic dataset from the specified input directory
train_df = pd.read_csv('./input/train.csv')

# --- Preprocessing (Common to both models) ---
# Drop columns that are not useful for prediction or require complex feature engineering for this simple example
train_df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

# Fill missing Age values with the median
train_df['Age'].fillna(train_df['Age'].median(), inplace=True)

# Fill missing Embarked values with the mode
train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)

# Convert 'Sex' to numerical: 'male' to 0, 'female' to 1
train_df['Sex'] = train_df['Sex'].map({'male': 0, 'female': 1})

# One-hot encode 'Embarked' and 'Pclass' categorical features
# drop_first=True avoids multicollinearity, though not strictly necessary for simple models,
# it's good practice for tree-based models and general ML.
train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass'], drop_first=True)

# Define features (X) and target (y)
X = train_df.drop('Survived', axis=1)
y = train_df['Survived']

# Split data into training and validation sets
# A test_size of 0.2 means 20% of the data will be used for validation
# random_state ensures reproducibility of the split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Model Training ---

# 1. Initialize and Train the XGBoost Classifier (from base solution)
xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
xgb_clf.fit(X_train, y_train)

# 2. Initialize and Train the LightGBM Classifier (from reference solution)
lgb_clf = lgb.LGBMClassifier(objective='binary', random_state=42)
lgb_clf.fit(X_train, y_train)

# --- Prediction and Ensembling ---

# Get prediction probabilities from XGBoost
# We take the probability of the positive class (survival, which is class 1)
y_pred_proba_xgb = xgb_clf.predict_proba(X_val)[:, 1]

# Get prediction probabilities from LightGBM
# We take the probability of the positive class (survival, which is class 1)
y_pred_proba_lgb = lgb_clf.predict_proba(X_val)[:, 1]

# Ensemble the predictions using a simple average of probabilities
# Average the probabilities from both models
y_pred_proba_ensemble = (y_pred_proba_xgb + y_pred_proba_lgb) / 2

# Convert averaged probabilities to binary predictions (0 or 1)
# A threshold of 0.5 is commonly used for binary classification
y_pred_ensemble = (y_pred_proba_ensemble >= 0.5).astype(int)

# --- Evaluation ---

# Evaluate accuracy of the ensembled model on the validation set
accuracy_ensemble = accuracy_score(y_val, y_pred_ensemble)

# Print the final validation performance in the required format
print(f"Final Validation Performance: {accuracy_ensemble:.4f}")

